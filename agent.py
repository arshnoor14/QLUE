"""
agent.py
--------
DataFluent Agent Backend.
Features: Strict API Routing, Dynamic Schema Extraction, SQL Critic,
Self-Healing Loops, RAG, and automated ITR Compliance Audits.
"""

import os
import re
from typing import TypedDict, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

load_dotenv(override=True)

DEFAULT_DB_PATH = "sales_data.db"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_TIMEOUT = float(os.getenv("GROQ_TIMEOUT", "20"))
RAG_DOC_PATH = "sales_policies.txt"


class GraphState(TypedDict):
    user_question: str
    db_path: str
    intent: Optional[str]
    database_schema: Optional[str]
    sql_query: Optional[str]
    sql_result: Optional[str]
    rag_context: Optional[str]
    final_result: Optional[str]
    error: Optional[str]
    retry_count: int


def get_engine(db_path: str):
    return create_engine(f"sqlite:///{db_path}", poolclass=NullPool, echo=False)


def get_llm(temperature: float = 0):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env or environment.")
    return ChatGroq(
        model=GROQ_MODEL,
        temperature=temperature,
        groq_api_key=api_key,
        timeout=GROQ_TIMEOUT,
        max_retries=1,
    )


def retrieve_sales_policy(question: str) -> str:
    if not os.path.exists(RAG_DOC_PATH):
        return "Warning: Corporate policy rules (sales_policies.txt) not found."
    with open(RAG_DOC_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("## ")
    intro = sections[0]
    matched = []
    question_lower = question.lower()
    keywords = re.findall(r'\b\w{4,}\b', question_lower)

    for sec in sections[1:]:
        lines = sec.splitlines()
        header = lines[0].lower() if lines else ""
        body = sec.lower()
        score = sum(1 for kw in keywords if kw in header) * 3 + sum(1 for kw in keywords if kw in body)
        if score > 0:
            matched.append((score, sec))

    if matched:
        matched.sort(key=lambda x: x[0], reverse=True)
        return intro + "\n" + "\n".join("## " + item[1] for item in matched[:2])
    return content


ROUTER_SYSTEM_PROMPT = """You are an intelligent query router.
Classify the user's question into ONLY ONE of four categories:
1. 'compliance_audit': If the user explicitly asks to evaluate their data, check thresholds, or suggest which ITR form they should file.
2. 'sql': If the question requires querying data, totals, metrics, or row listings from a database.
3. 'rag': If the question asks about general return policies, shipping rates, or static guidelines.
4. 'general': If the question is a greeting or general chat.

Output ONLY the exact category word. No explanation."""


def intent_router_node(state: GraphState) -> GraphState:
    q = state["user_question"].lower()
    if any(k in q for k in ["itr", "file tax", "tax return", "suggest itr", "compliance audit", "audit"]):
        return {**state, "intent": "compliance_audit", "error": None}

    try:
        llm = get_llm(temperature=0)
        response = llm.invoke([SystemMessage(content=ROUTER_SYSTEM_PROMPT), HumanMessage(content=state["user_question"])])
        raw = response.content.strip().lower()
        match = re.search(r'\b(sql|rag|compliance_audit|general)\b', raw)
        return {**state, "intent": match.group(0) if match else "sql", "error": None}
    except Exception as e:
        return {**state, "intent": "sql", "error": f"API Router Error: {str(e)}"}


def schema_node(state: GraphState) -> GraphState:
    try:
        engine = get_engine(state["db_path"])
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        if not table_names:
            return {**state, "database_schema": "Database is empty.", "error": "No tables found in the uploaded file."}

        schema_parts = []
        for table in table_names:
            columns = inspector.get_columns(table)
            col_lines = [f"  - {col['name']} ({str(col['type'])})" for col in columns]
            schema_parts.append(f"Table: {table}\n" + "\n".join(col_lines))
        return {**state, "database_schema": "\n\n".join(schema_parts), "error": None}
    except Exception as e:
        return {**state, "error": f"Schema Extraction Error: {str(e)}"}


SQL_SYSTEM_PROMPT = """You are an expert SQL assistant.
Your ONLY output must be a single, valid SQLite SQL query string based on the schema provided.
No explanations, no conversational text, no markdown code fences (no ```sql or ``` wrapping).
Output raw SQL only."""


def groq_sql_node(state: GraphState) -> GraphState:
    if state.get("error"):
        return state
    user_prompt = f"Schema:\n{state['database_schema']}\n\nQuestion: {state['user_question']}\nReturn ONLY raw SQLite query."
    try:
        llm = get_llm(temperature=0)
        response = llm.invoke([SystemMessage(content=SQL_SYSTEM_PROMPT), HumanMessage(content=user_prompt)])
        return {**state, "sql_query": clean_sql_string(response.content.strip()), "error": None}
    except Exception as e:
        return {**state, "error": f"Groq API SQL Generation Error: {str(e)}"}


CRITIC_SYSTEM_PROMPT = """You are an expert SQL reviewer.
Review the proposed SQL query against the schema. Correct any invalid column names or syntax errors.
Output ONLY the finalized raw SQLite query string. No markdown, no explanation."""


def critic_node(state: GraphState) -> GraphState:
    if state.get("error") or not state.get("sql_query"):
        return state
    prompt = f"Schema:\n{state['database_schema']}\nQuestion: {state['user_question']}\nProposed SQL:\n{state['sql_query']}"
    try:
        llm = get_llm(temperature=0)
        response = llm.invoke([SystemMessage(content=CRITIC_SYSTEM_PROMPT), HumanMessage(content=prompt)])
        return {**state, "sql_query": clean_sql_string(response.content.strip()), "error": None}
    except Exception:
        # If critic fails, proceed with the un-critiqued SQL rather than crashing
        return state


def execution_node(state: GraphState) -> GraphState:
    if state.get("error"):
        return state
    sql = (state.get("sql_query") or "").strip()
    if not sql:
        return {**state, "error": "No SQL query available to execute."}
    try:
        engine = get_engine(state["db_path"])
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())
        if not rows:
            final_table = "Query executed successfully but returned no rows."
        else:
            header = " | ".join(columns)
            divider = "-+-".join("-" * len(c) for c in columns)
            data_rows = [" | ".join(str(v) for v in row) for row in rows]
            final_table = "\n".join([header, divider, *data_rows])
        return {**state, "sql_result": final_table, "error": None}
    except Exception as e:
        return {**state, "error": str(e)}


def correct_sql_node(state: GraphState) -> GraphState:
    prompt = (
        f"Schema:\n{state['database_schema']}\n"
        f"Failed SQL:\n{state['sql_query']}\n"
        f"Error:\n{state['error']}\n"
        f"Return corrected raw SQLite SQL only. No markdown fences."
    )
    try:
        llm = get_llm(temperature=0)
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            **state,
            "sql_query": clean_sql_string(response.content.strip()),
            "retry_count": state["retry_count"] + 1,
            "error": None,
        }
    except Exception as e:
        return {
            **state,
            "retry_count": state.get("retry_count", 0) + 1,
            "error": f"API Correction failed: {str(e)}",
        }


def compliance_audit_node(state: GraphState) -> GraphState:
    try:
        engine = get_engine(state["db_path"])
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if not tables:
                return {**state, "error": "No data found for compliance audit."}
            target_table = tables[0]
            table_columns = [c["name"] for c in inspector.get_columns(target_table)]
            amt_col = next(
                (c for c in table_columns if any(k in c.lower() for k in ["amount", "sales", "revenue", "total", "price"])),
                None,
            )

            if amt_col:
                total_turnover = conn.execute(text(f'SELECT SUM("{amt_col}") FROM "{target_table}"')).scalar() or 0.0
                total_transactions = conn.execute(text(f'SELECT COUNT(*) FROM "{target_table}"')).scalar() or 0
            else:
                total_turnover, total_transactions = 0.0, 0

        rag_context = retrieve_sales_policy("ITR Guidelines")
        sql_result = (
            f"COMPUTED_METRICS:\n"
            f"- Mapped Gross Turnover: INR {total_turnover:,.2f}\n"
            f"- Scanned Transactions: {total_transactions}"
        )
        return {**state, "rag_context": rag_context, "sql_result": sql_result, "error": None}
    except Exception as e:
        return {**state, "error": f"Compliance auditing node fault: {str(e)}"}


def rag_node(state: GraphState) -> GraphState:
    return {**state, "rag_context": retrieve_sales_policy(state["user_question"]), "error": None}


def general_node(state: GraphState) -> GraphState:
    return {**state, "rag_context": "General chat interaction context.", "error": None}


def synthesis_node(state: GraphState) -> GraphState:
    # Hard-stop after max retries
    if state.get("error") and state.get("retry_count", 0) >= 3:
        return {**state, "final_result": f"❌ System encountered a critical error after retries: {state['error']}"}

    intent = state.get("intent", "sql")

    if intent == "compliance_audit":
        system_prompt = (
            "You are Qlue Audit Engine, an automated expert Tax Regulatory Consultant.\n"
            "Review the computed metrics summary from the data and map it to the active ITR Guidelines.\n"
            "Provide a clear, professional, structured audit report breaking down:\n"
            "1. ⚙️ DIAGNOSTIC ANALYSIS: Gross volume aggregates.\n"
            "2. 📋 REGULATORY FORM ASSIGNMENT: Suggest the exact ITR Form (ITR-1, ITR-3, or ITR-4).\n"
            "3. ⚖️ JUSTIFICATION: Precise reasoning matching threshold conditions from the knowledge document."
        )
        context = f"METRICS:\n{state.get('sql_result', 'No metrics available.')}\n\nITR CRITERIA:\n{state.get('rag_context', '')}"
    elif intent == "sql":
        system_prompt = (
            "You are Qlue, a friendly data assistant. "
            "Summarize the SQL query results clearly in plain English. "
            "Do not show the raw table or the SQL — just explain the insights."
        )
        context = f"SQL used:\n{state.get('sql_query', '')}\n\nTable results:\n{state.get('sql_result', 'No results.')}"
    else:
        system_prompt = "You are Qlue Systems. Respond professionally to the user's question based on the context provided."
        context = f"Context:\n{state.get('rag_context', '')}"

    try:
        llm = get_llm(temperature=0.2)
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {state['user_question']}\n\nContext:\n{context}"),
        ])
        return {**state, "final_result": response.content.strip(), "error": None}
    except Exception as e:
        fallback = f"⚠️ API error during synthesis.\n\nRaw data:\n{state.get('sql_result', 'No result generated.')}"
        return {**state, "final_result": fallback, "error": str(e)}


# ── Graph Routing ─────────────────────────────────────────────────────────────

def route_by_intent(state: GraphState) -> str:
    intent = state.get("intent", "sql")
    if intent == "compliance_audit":
        return "compliance_audit_node"
    elif intent == "rag":
        return "rag_node"
    elif intent == "general":
        return "general_node"
    return "schema_node"


def route_execution_result(state: GraphState) -> str:
    if state.get("error"):
        if not state.get("sql_query"):
            return "synthesis_node"
        if state.get("retry_count", 0) < 3:
            return "correct_sql_node"
        else:
            return "synthesis_node"
    return "synthesis_node"


def clean_sql_string(sql: str) -> str:
    """Strip markdown fences and whitespace from LLM SQL output."""
    sql = sql.strip()
    # Remove ```sql ... ``` or ``` ... ``` fences
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql)
    # Remove lone backticks
    sql = sql.replace("`", "")
    # Strip 'sql\n' prefix that some models add
    if sql.lower().startswith("sql\n"):
        sql = sql[4:]
    return sql.strip()


def build_graph():
    builder = StateGraph(GraphState)
    builder.add_node("intent_router_node",    intent_router_node)
    builder.add_node("schema_node",           schema_node)
    builder.add_node("groq_sql_node",         groq_sql_node)
    builder.add_node("critic_node",           critic_node)
    builder.add_node("execution_node",        execution_node)
    builder.add_node("correct_sql_node",      correct_sql_node)
    builder.add_node("compliance_audit_node", compliance_audit_node)
    builder.add_node("rag_node",              rag_node)
    builder.add_node("general_node",          general_node)
    builder.add_node("synthesis_node",        synthesis_node)

    builder.add_edge(START, "intent_router_node")
    builder.add_conditional_edges(
        "intent_router_node",
        route_by_intent,
        {
            "schema_node":           "schema_node",
            "compliance_audit_node": "compliance_audit_node",
            "rag_node":              "rag_node",
            "general_node":          "general_node",
        },
    )

    builder.add_edge("schema_node",    "groq_sql_node")
    builder.add_edge("groq_sql_node",  "critic_node")
    builder.add_edge("critic_node",    "execution_node")
    builder.add_conditional_edges(
        "execution_node",
        route_execution_result,
        {
            "correct_sql_node": "correct_sql_node",
            "synthesis_node":   "synthesis_node",
        },
    )
    builder.add_edge("correct_sql_node",      "execution_node")
    builder.add_edge("compliance_audit_node", "synthesis_node")
    builder.add_edge("rag_node",              "synthesis_node")
    builder.add_edge("general_node",          "synthesis_node")
    builder.add_edge("synthesis_node",        END)
    return builder.compile()


def run_agent(question: str, db_path: str = DEFAULT_DB_PATH) -> dict:
    graph = build_graph()
    return graph.invoke({
        "user_question":   question,
        "db_path":         db_path,
        "intent":          None,
        "database_schema": None,
        "sql_query":       None,
        "sql_result":      None,
        "rag_context":     None,
        "final_result":    None,
        "error":           None,
        "retry_count":     0,
    })


def generate_and_critic_sql(question: str, db_path: str = DEFAULT_DB_PATH) -> dict:
    state = schema_node({
        "user_question":   question,
        "db_path":         db_path,
        "database_schema": None,
        "error":           None,
        "intent":          "sql",
        "sql_query":       None,
        "sql_result":      None,
        "rag_context":     None,
        "final_result":    None,
        "retry_count":     0,
    })
    state = groq_sql_node(state)
    return critic_node(state)


def execute_and_explain_sql(
    question: str, db_path: str, sql_query: str, database_schema: str = ""
) -> dict:
    state = {
        "user_question":   question,
        "db_path":         db_path,
        "intent":          "sql",
        "database_schema": database_schema,
        "sql_query":       sql_query,
        "sql_result":      None,
        "rag_context":     None,
        "final_result":    None,
        "retry_count":     0,
        "error":           None,
    }
    state = execution_node(state)
    while state.get("error") and state.get("retry_count", 0) < 3:
        state = correct_sql_node(state)
        state = execution_node(state)
    return synthesis_node(state)
