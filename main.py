"""
main.py
-------
Qlue Minimalist Tech Workspace UI.
Pure User-Upload Data Logic with Brutalist wireframes, solid borders,
and clean API-strict state management.
"""

import re
import os
import sqlite3
import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv(override=True)
from agent import (
    run_agent,
    generate_and_critic_sql,
    execute_and_explain_sql,
    get_engine,
    intent_router_node,
)

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Qlue · System Interface",
    page_icon="⚫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="stApp"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #ffffff !important;
    color: #000000 !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #ffffff;
}
::-webkit-scrollbar-thumb {
    background: #e5e7eb;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #cbd5e1;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #fafafa !important;
    border-right: 1px solid #000000 !important;
}
[data-testid="stSidebar"] * {
    color: #000000 !important;
}

/* Header/Hero Styling */
.hero-container {
    background-color: #ffffff;
    border-bottom: 1px solid #000000;
    padding: 35px 0px 24px 0px;
    margin-bottom: 30px;
}
.hero-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    color: #7a7a7a;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-weight: 600;
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 0.95;
    color: #000000;
    text-transform: uppercase;
    margin: 0 0 12px 0;
}
.hero-sub {
    color: #000000;
    font-size: 1.1rem;
    font-style: italic;
    margin: 0;
}

/* Custom Minimal Cards */
.glass-card {
    background-color: #ffffff;
    border: 1px solid #000000;
    border-radius: 0px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: none;
    transition: all 0.2s ease;
}
.glass-card:hover {
    background-color: #fcfcfc;
}

/* Custom metrics cards */
div[data-testid="metric-container"] {
    background-color: #ffffff !important;
    border: 1px solid #000000 !important;
    border-radius: 0px !important;
    padding: 16px 20px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}
div[data-testid="metric-container"]:hover {
    background-color: #fafafa !important;
}
div[data-testid="metric-container"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #7a7a7a !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #000000 !important;
    letter-spacing: -0.03em;
}

/* Terminal SQL Code Blocks */
.sql-block {
    background: #f9f9f9;
    border: 1px solid #000000;
    border-radius: 0px;
    padding: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: #000000;
    white-space: pre-wrap;
    margin: 14px 0;
}

/* Pill indicators */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 10px;
    border: 1px solid #000000;
    background-color: #ffffff;
    color: #000000;
    margin-bottom: 12px;
    font-weight: 500;
}

/* Streamlit Component Styles */
[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #000000 !important;
    border-radius: 0px !important;
    padding: 20px !important;
    margin: 12px 0 !important;
    box-shadow: none !important;
}

div.stTextInput > div > div > input {
    background-color: #ffffff !important;
    border: 1px solid #000000 !important;
    border-radius: 0px !important;
    color: #000000 !important;
    padding: 12px 16px !important;
}
div.stTextInput > div > div > input:focus {
    border-color: #000000 !important;
    box-shadow: none !important;
}

button[data-baseweb="tab"] {
    font-size: 0.92rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: #7a7a7a !important;
    border-bottom: 2px solid transparent !important;
    padding: 12px 20px !important;
    transition: all 0.2s ease !important;
}
button[aria-selected="true"] {
    color: #000000 !important;
    border-bottom-color: #000000 !important;
    font-weight: 600 !important;
    background: #ffffff !important;
}

/* Custom layout blocks */
form[key="chat_form_brutalist"] {
    background-color: #ffffff !important;
    border: 1px solid #000000 !important;
    border-radius: 0px !important;
    padding: 16px !important;
}

/* Badges styling */
.badge-custom {
    display: inline-block;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    border: 1px solid #000000;
    border-radius: 0px;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    background-color: #ffffff;
    color: #000000;
    margin-bottom: 8px;
}
.badge-success { background-color: #ffffff; border-color: #000000; color: #000000; }
.badge-warning { background-color: #ffffff; border-color: #000000; color: #000000; }
.badge-danger { background-color: #ffffff; border-color: #000000; color: #000000; }
.badge-info { background-color: #ffffff; border-color: #000000; color: #000000; }
</style>
""", unsafe_allow_html=True)

# ── Session State Initialisation ──────────────────────────────────────────────
def _init_state():
    defaults = {
        "history":            [],
        "query_count":        0,
        "db_path":            "sales_data.db",
        "has_data":           False,
        "insights":           {},
        "pending_hitl":       None,
        "prefill":            "",
        "selected_question":  ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── Safe Insights Calculation ─────────────────────────────────────────────────
def _calc_insights_from_df(df: pd.DataFrame):
    insights = {"total_rows": len(df)}
    amt_cols = [c for c in df.columns if any(k in c.lower() for k in ["amount", "sales", "revenue", "total", "price"])]
    if amt_cols:
        try:
            insights["total_revenue"] = float(pd.to_numeric(df[amt_cols[0]], errors="coerce").sum())
        except Exception:
            insights["total_revenue"] = 0.0
    else:
        insights["total_revenue"] = 0.0
    st.session_state.insights = insights


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Qlue Control")
    st.markdown("---")

    hitl_enabled = st.checkbox("Enable Human-in-the-Loop Gateway", value=False)

    st.markdown("---")
    st.markdown("<span style='font-family:JetBrains Mono,monospace;font-size:0.75rem;color:#7a7a7a;font-weight:600;'>INJECT USER FILES</span>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Excel or CSV Dataset:", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            # STEP 1 — READ FILE
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)

            # STEP 2 — CLEAN COLUMN NAMES
            df_upload.columns = [
                col.strip().lower().replace(" ", "_")
                for col in df_upload.columns
            ]

            # STEP 3 — SHOW DEBUG INFO
            st.success("✅ File uploaded successfully.")
            
            with st.expander("🛠️ File Verification Info", expanded=False):
                st.write("### Preview of Uploaded Dataset")
                st.dataframe(df_upload.head(), use_container_width=True)

                st.write("### Dataset Shape")
                st.write(df_upload.shape)

                st.write("### Column Names")
                st.write(df_upload.columns.tolist())

                st.write("### Data Types")
                st.write(df_upload.dtypes)

            # STEP 4 — SAVE TO SQLITE
            conn = sqlite3.connect("sales_data.db")
            df_upload.to_sql(
                "sales",
                conn,
                if_exists="replace",
                index=False
            )
            conn.close()

            # STEP 5 — VERIFY DATABASE
            verify_conn = sqlite3.connect("sales_data.db")
            verification_df = pd.read_sql_query(
                "SELECT * FROM sales LIMIT 5",
                verify_conn
            )
            verify_conn.close()

            with st.expander("🗄️ SQLite Verification Preview", expanded=False):
                st.dataframe(verification_df, use_container_width=True)

            # STEP 6 — SESSION STATE
            st.session_state.db_path = "sales_data.db"
            st.session_state.has_data = True

            _calc_insights_from_df(df_upload)
            st.success("✅ private database created successfully.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Upload Error: {str(e)}")

    st.markdown("---")
    if st.button("Clear Engine States", use_container_width=True):
        st.session_state.history      = []
        st.session_state.query_count  = 0
        st.session_state.pending_hitl = None
        st.session_state.has_data     = False
        if os.path.exists("sales_data.db"):
            try:
                os.remove("sales_data.db")
            except Exception:
                pass
        st.rerun()

# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
  <div class="hero-title">Welcome to Qlue.</div>
  <p class="hero-sub">"Ask anything about your data in plain English." — No SQL. No Setup. Just Answers.</p>
</div>
""", unsafe_allow_html=True)

# ── Blank State ───────────────────────────────────────────────────────────────
if not st.session_state.has_data:
    st.markdown("<br><br>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        st.markdown("""
        <div class="glass-card" style="height:100%;">
            <div style="font-size: 2.2rem; font-weight: 700; color: #000000;">01</div>
            <div style="font-family:JetBrains Mono,monospace; font-size:0.75rem; text-transform:uppercase; color:#7a7a7a; margin: 10px 0;">Upload Your Data</div>
            <p style="color:#000000; font-size:0.9rem; margin-top:8px;">Drag and drop any business Excel or CSV file in the sidebar or upload zone to initialize your private workspace.</p>
        </div>
        """, unsafe_allow_html=True)
    with b_col2:
        st.markdown("""
        <div class="glass-card" style="height:100%;">
            <div style="font-size: 2.2rem; font-weight: 700; color: #000000;">02</div>
            <div style="font-family:JetBrains Mono,monospace; font-size:0.75rem; text-transform:uppercase; color:#7a7a7a; margin: 10px 0;">Type Your Question</div>
            <p style="color:#000000; font-size:0.9rem; margin-top:8px;">Ask anything about business records, commission rates, refund rules, or compliance criteria in plain English.</p>
        </div>
        """, unsafe_allow_html=True)
    with b_col3:
        st.markdown("""
        <div class="glass-card" style="height:100%;">
            <div style="font-size: 2.2rem; font-weight: 700; color: #000000;">03</div>
            <div style="font-family:JetBrains Mono,monospace; font-size:0.75rem; text-transform:uppercase; color:#7a7a7a; margin: 10px 0;">Dashboard Appears</div>
            <p style="color:#000000; font-size:0.9rem; margin-top:8px;">Advanced metrics, interactive analytical charts, and automated Indian tax compliance rules are computed instantly.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📥 Private Workspace Initializer")
    main_upload = st.file_uploader("Upload CSV or XLSX Excel sheet here to begin:", type=["csv", "xlsx"], key="main_body_uploader")
    if main_upload is not None:
        try:
            if main_upload.name.endswith(".csv"):
                df_upload = pd.read_csv(main_upload)
            else:
                df_upload = pd.read_excel(main_upload)
            df_upload.columns = [col.strip().lower().replace(" ", "_") for col in df_upload.columns]
            conn = sqlite3.connect("sales_data.db")
            df_upload.to_sql("sales", conn, if_exists="replace", index=False)
            conn.close()
            
            st.session_state.db_path = "sales_data.db"
            st.session_state.has_data = True
            _calc_insights_from_df(df_upload)
            st.success("✅ private database created successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Upload Error: {str(e)}")

    st.stop()

# ── Active Workspace Metrics ──────────────────────────────────────────────────
if st.session_state.insights:
    rows = st.session_state.insights.get("total_rows", 0)
    rev  = st.session_state.insights.get("total_revenue", 0.0)
    
    st.markdown(f"""
    <div style="display:flex; gap:20px; margin-bottom:20px;">
        <div style="flex:1; background-color:#ffffff; border:1px solid #000000; padding:16px 22px; box-shadow: none;">
            <div style="font-family:'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; color: #7a7a7a; letter-spacing: 0.08em;">01 // Total Rows Loaded</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #000000; margin-top:5px; letter-spacing:-0.03em;">{rows:,}</div>
        </div>
        <div style="flex:1; background-color:#ffffff; border:1px solid #000000; padding:16px 22px; box-shadow: none;">
            <div style="font-family:'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; color: #7a7a7a; letter-spacing: 0.08em;">02 // Turnover Scanned</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #000000; margin-top:5px; letter-spacing:-0.03em;">INR {rev:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Core Helper Functions ──────────────────────────────────────────────────────
def get_schema_text(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema_text = ""
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema_text += f"\nTABLE: {table_name}\n"
        for col in columns:
            schema_text += f"- {col[1]} ({col[2]})\n"
    conn.close()
    return schema_text

def generate_sql_query(question, schema):
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    system_prompt = """
You are a SQLite expert.

Convert the user's question into a valid SQLite query.

CRITICAL RULES:
- Use ONLY SQLite syntax
- NEVER use PostgreSQL/MySQL functions
- NEVER use EXTRACT()
- For dates use:
  strftime('%Y', column)
  strftime('%m', column)

- Use ONLY existing columns
- Use ONLY existing tables
- Return ONLY raw SQL
- No markdown
- No explanations
"""

    user_prompt = f"""
    DATABASE SCHEMA:
    {schema}

    USER QUESTION:
    {question}
    """

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    sql_query = response.content.strip()
    sql_query = sql_query.replace("```sql", "")
    sql_query = sql_query.replace("```", "")
    return sql_query.strip()

def generate_ai_dashboard_summary(df):
    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if len(numeric_cols) == 0:
            return

        revenue_col = numeric_cols[0]

        product_col = None
        for col in df.columns:
            if any(k in col.lower() for k in ["product", "item", "category"]):
                product_col = col
                break

        time_col = None
        for col in df.columns:
            if any(k in col.lower() for k in ["month", "date", "year"]):
                time_col = col
                break

        total_revenue = df[revenue_col].sum()
        avg_revenue = df[revenue_col].mean()
        max_revenue = df[revenue_col].max()
        total_records = len(df)

        top_products_text = "No product data available."
        if product_col:
            product_summary = df.groupby(product_col)[revenue_col].sum().sort_values(ascending=False).head(5)
            top_products_text = product_summary.to_string()

        trend_text = "No trend data available."
        if time_col:
            trend_summary = df.groupby(time_col)[revenue_col].sum()
            trend_text = trend_summary.to_string()

        llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        system_prompt = """
You are a senior AI business intelligence analyst.

Your job is to analyze ONLY the provided business data.

STRICT RULES:
- Do NOT invent information
- Do NOT suggest unrealistic business strategies
- Do NOT assume industries or markets
- ONLY mention observations supported by data
- Be concise and analytical
- Focus on trends, growth, declines, and performance
- Use exact numbers when possible

Provide:
1. Business observations
2. Revenue trends
3. Product/category insights
4. Data-driven recommendations

Recommendations must be directly tied to the data.
"""

        user_prompt = f"""
        BUSINESS METRICS
        Total Revenue: {total_revenue}
        Average Revenue: {avg_revenue}
        Maximum Revenue: {max_revenue}
        Total Records: {total_records}

        TOP PRODUCTS:
        {top_products_text}

        SALES TRENDS:
        {trend_text}
        """

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        st.write("## 🧠 AI Business Analysis")
        st.success(response.content)

    except Exception as e:
        st.error(f"AI Summary Error: {str(e)}")

def detect_business_anomalies(df):
    st.write("## 🚨 Business Risk Detection")
    try:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if len(numeric_cols) == 0:
            return

        revenue_col = numeric_cols[0]

        time_col = None
        for col in df.columns:
            if any(k in col.lower() for k in ["year", "month", "date"]):
                time_col = col
                break

        # Revenue Drop Detection
        if time_col:
            trend_df = df.groupby(time_col)[revenue_col].sum().reset_index()
            trend_df = trend_df.sort_values(time_col)
            revenues = trend_df[revenue_col].tolist()
            periods = trend_df[time_col].tolist()

            for i in range(1, len(revenues)):
                previous = revenues[i - 1]
                current = revenues[i]
                if previous == 0:
                    continue
                change_pct = ((current - previous) / previous) * 100

                if change_pct < -5:
                    st.error(f"⚠️ Revenue dropped {abs(change_pct):.1f}% from {periods[i-1]} to {periods[i]}")
                elif change_pct > 5:
                    st.success(f"📈 Revenue increased {change_pct:.1f}% from {periods[i-1]} to {periods[i]}")

        # Revenue Concentration
        category_col = None
        for col in df.columns:
            if any(k in col.lower() for k in ["product", "category", "item"]):
                category_col = col
                break

        if category_col:
            category_summary = df.groupby(category_col)[revenue_col].sum().sort_values(ascending=False)
            total_revenue = category_summary.sum()
            if total_revenue > 0:
                top_share = (category_summary.iloc[0] / total_revenue) * 100
                top_category = category_summary.index[0]
                if top_share > 50:
                    st.warning(f"⚠️ Revenue concentration risk: **{top_category}** contributes **{top_share:.1f}%** of total revenue.")

        # Volatility Detection
        std_dev = df[revenue_col].std()
        avg_rev = df[revenue_col].mean()
        if avg_rev > 0:
            volatility = (std_dev / avg_rev) * 100
            if volatility > 100:
                st.warning(f"⚠️ High revenue volatility detected ({volatility:.1f}%).")

    except Exception as e:
        st.error(f"Anomaly Detection Error: {str(e)}")

def run_sql_query(sql_query, db_path):
    conn = sqlite3.connect(db_path)
    df_result = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df_result

def auto_visualize(df):
    if df.empty:
        st.warning("No data available for visualization.")
        return

    numeric_cols = []
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="ignore")
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_cols.append(col)
        except:
            pass

    if len(df.columns) < 2 or len(numeric_cols) == 0:
        st.info("Visualization skipped: insufficient columns.")
        return

    category_col = df.columns[0]
    numeric_col = numeric_cols[0]
    viz_df = df[[category_col, numeric_col]].dropna()

    if viz_df.empty:
        st.info("Visualization skipped: no plottable data.")
        return

    st.write("## 📊 Auto Visualization")
    time_keywords = ["date", "month", "year", "day"]
    try:
        if any(k in category_col.lower() for k in time_keywords):
            st.line_chart(viz_df.set_index(category_col))
        else:
            st.bar_chart(viz_df.set_index(category_col))
    except Exception as e:
        st.error(f"Visualization Error: {str(e)}")

def show_kpi_cards(df):
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) == 0:
        return

    st.write("## 📌 Key Metrics")
    cols = st.columns(min(3, len(numeric_cols)))
    for i, col in enumerate(numeric_cols[:3]):
        total_value = df[col].sum()
        avg_value = df[col].mean()
        max_value = df[col].max()
        with cols[i]:
            st.metric(label=f"Total {col}", value=f"{total_value:,.2f}")
            st.metric(label=f"Average {col}", value=f"{avg_value:,.2f}")
            st.metric(label=f"Max {col}", value=f"{max_value:,.2f}")

def generate_basic_insights(df):
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) == 0:
        return

    st.write("## 🧠 AI Business Insights")
    for col in numeric_cols:
        total = df[col].sum()
        avg = df[col].mean()
        highest = df[col].max()
        st.success(
            f"""
            • Total {col} is {total:,.2f}
            • Average {col} is {avg:,.2f}
            • Highest recorded {col} is {highest:,.2f}
            """
        )

def show_query_suggestions():
    suggestions = [
        "What is total revenue?",
        "Show revenue by product",
        "Which product sells the most?",
        "Show monthly sales trend",
        "Top 5 customers by revenue",
        "Which month had highest sales?"
    ]
    cols = st.columns(3)
    for i, question in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(f"› {question}", key=f"sug_{i}", use_container_width=True):
                st.session_state.selected_question = question
                st.rerun()

# ── Tabs Architecture ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 AI Chat Assistant",
    "🔍 SQL Query Explorer",
    "📊 Smart Business Dashboard",
    "🗄️ Database Inspector",
    "⚖️ AI Compliance & Tax Copilot",
    "🗺️ System Architecture"
])

# ── Tab 1: AI Chat Assistant ──────────────────────────────────────────────────
with tab1:
    # Render chat history
    for msg in st.session_state.history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"**USER**<br>{msg['content']}", unsafe_allow_html=True)
        elif msg["role"] == "agent":
            with st.chat_message("assistant"):
                badge = msg.get("intent", "general")
                if badge == "sql":
                    st.markdown('<span class="badge-custom badge-info">GEN_ENGINE // SQL_INJECTOR</span>', unsafe_allow_html=True)
                elif badge == "compliance_audit":
                    st.markdown('<span class="badge-custom badge-warning">TAX_ENGINE // REGULATORY_AUDIT</span>', unsafe_allow_html=True)
                elif badge == "rag":
                    st.markdown('<span class="badge-custom badge-success">DOC_ENGINE // RAG_RETRIEVER</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-custom badge-info">SYS_LOG // DIALOGUE</span>', unsafe_allow_html=True)

                st.markdown(msg.get("content") or "⚠️ Empty payload received.")

                if badge == "sql" and msg.get("sql"):
                    with st.expander("🔍 Query Inspector // Generated SQL & Results", expanded=False):
                        st.markdown(f'<div class="sql-block">{msg["sql"]}</div>', unsafe_allow_html=True)
                        raw = msg.get("raw_table", "")
                        if raw and "returned no rows" not in raw:
                            try:
                                lines = [l.strip() for l in raw.splitlines() if l.strip()]
                                if len(lines) >= 3:
                                    header_cols = [c.strip() for c in lines[0].split("|") if c.strip()]
                                    rows_list = []
                                    for line in lines[2:]:
                                        if "|" in line:
                                            rows_list.append([c.strip() for c in line.split("|")])
                                    if rows_list:
                                        df_res = pd.DataFrame(rows_list, columns=header_cols)
                                        st.dataframe(df_res, hide_index=True, use_container_width=True)
                            except Exception:
                                st.text(raw)

    # ── HITL Gateway ──────────────────────────────────────────────────────────
    if st.session_state.pending_hitl:
        pending = st.session_state.pending_hitl
        with st.chat_message("assistant"):
            st.markdown('<span class="badge-custom badge-danger">CRITICAL SYSTEM LOCK // BREAKPOINT</span>', unsafe_allow_html=True)
            st.markdown("### 🛑 Gate Intercept: Execution Approval Required")
            edited_sql = st.text_area("SQL Schema Compiler Box:", value=pending["sql"], height=130, key="hitl_sql_box")
            btn_col1, _, _ = st.columns([2.5, 2.5, 7])
            with btn_col1:
                if st.button("Execute Transaction", use_container_width=True, key="exec_hitl"):
                    result = execute_and_explain_sql(
                        pending["question"],
                        st.session_state.db_path,
                        edited_sql,
                        pending["schema"],
                    )
                    st.session_state.history.append({
                        "role":      "agent",
                        "content":   result.get("final_result"),
                        "intent":    "sql",
                        "sql":       edited_sql,
                        "raw_table": result.get("sql_result"),
                    })
                    st.session_state.pending_hitl = None
                    st.rerun()

    # ── Pre-configured query injectors ────────────────────────────────────────
    st.markdown("<br><span style='font-family:JetBrains Mono,monospace;font-size:0.75rem;color:#7a7a7a;font-weight:600;'>QUERY INJECTORS // PRE-CONFIGURED</span>", unsafe_allow_html=True)
    col_inj1, col_inj2 = st.columns(2)
    with col_inj1:
        if st.button("› 📑 RUN AUTOMATED TAX COMPLIANCE AUDIT (SUGGEST ITR)", use_container_width=True, key="inj_audit"):
            st.session_state.prefill = "Analyze my file variables and tell me which Indian Income Tax Return (ITR) form I should file."
            st.rerun()
    with col_inj2:
        if st.button("› 📑 INQUIRE ABOUT PLATFORM COMMISSIONS & REFUNDS", use_container_width=True, key="inj_comm"):
            st.session_state.prefill = "What are the platform commission fees, refund processing times, and rules for barter transactions?"
            st.rerun()

    prefill_val = st.session_state.prefill
    st.session_state.prefill = ""

    # Chat Input Form
    with st.form(key="chat_form_brutalist", clear_on_submit=True):
        f_c1, f_c2 = st.columns([9.5, 1.5])
        with f_c1:
            user_input = st.text_input(
                "Prompt Input String",
                value=prefill_val,
                placeholder="Ask about dataset records, platform rules, or tax guidelines...",
                label_visibility="collapsed",
            )
        with f_c2:
            submitted = f_c2.form_submit_button("Ask Agent ⚡", use_container_width=True)

    if submitted and user_input.strip():
        if not os.getenv("GROQ_API_KEY"):
            st.error("🔑 ERROR: 'GROQ_API_KEY' missing from environment / .env file.")
            st.stop()

        question = user_input.strip()
        st.session_state.history.append({"role": "user", "content": question})
        st.session_state.query_count += 1

        router_state = {
            "user_question":   question,
            "db_path":         st.session_state.db_path,
            "intent":          None,
            "database_schema": None,
            "sql_query":       None,
            "sql_result":      None,
            "rag_context":     None,
            "final_result":    None,
            "error":           None,
            "retry_count":     0,
        }

        with st.spinner("Routing query..."):
            routed = intent_router_node(router_state)

        intent = routed.get("intent", "sql")

        if intent == "sql" and hitl_enabled:
            with st.spinner("Compiling and verifying SQL via Groq API..."):
                gen_state = generate_and_critic_sql(question, st.session_state.db_path)
            if gen_state.get("error"):
                st.error(f"API Error during SQL generation: {gen_state['error']}")
                st.stop()
            st.session_state.pending_hitl = {
                "question": question,
                "sql":      gen_state.get("sql_query", ""),
                "schema":   gen_state.get("database_schema", ""),
            }
        else:
            try:
                with st.spinner("Processing via AI Agent..."):
                    result = run_agent(question, st.session_state.db_path)
            except Exception as e:
                st.error(f"💥 AGENT CRASH: {str(e)}")
                result = {
                    "error": f"Agent crashed: {str(e)}",
                    "final_result": None,
                    "intent": "general",
                    "sql_query": None,
                    "sql_result": None
                }

            if result.get("error") and not result.get("final_result"):
                st.error(f"Agent Error: {result['error']}")

            st.session_state.history.append({
                "role":      "agent",
                "content":   result.get("final_result") or f"⚠️ No output generated. Error: {result.get('error')}",
                "intent":    result.get("intent"),
                "sql":       result.get("sql_query"),
                "raw_table": result.get("sql_result"),
            })

        st.rerun()

# ── Tab 2: SQL Query Explorer ─────────────────────────────────────────────────
with tab2:
    st.markdown("## 🔍 Relational Query Sandbox")
    st.markdown("Enter any analytical query in plain English. The system compiles a valid SQLite query, executes it, and renders immediate data charts and insights.")
    
    st.markdown("### Suggested Analytical Questions")
    show_query_suggestions()

    exp_question = st.text_input(
        "Ask a specific question about your data:",
        value=st.session_state.selected_question,
        key="explorer_query_input"
    )

    if st.button("Compile & Run Query ⚡", key="run_explorer_query", use_container_width=True):
        if not exp_question.strip():
            st.warning("Please type or select a question first.")
        else:
            with st.spinner("Compiling database schema..."):
                try:
                    schema = get_schema_text(st.session_state.db_path)
                    sql_query = generate_sql_query(exp_question, schema)
                    
                    st.markdown("### 🛠️ Mapped SQL Query")
                    st.code(sql_query, language="sql")
                    
                    result_df = run_sql_query(sql_query, st.session_state.db_path)
                    
                    st.markdown("### 📊 Query Execution Records")
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Run metrics & visualizations for this query
                    show_kpi_cards(result_df)
                    auto_visualize(result_df)
                    generate_basic_insights(result_df)
                    generate_ai_dashboard_summary(result_df)
                    detect_business_anomalies(result_df)
                    
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")

# ── Tab 3: Smart Business Dashboard ───────────────────────────────────────────
with tab3:
    st.markdown("## 📊 Interactive BI Dashboard")

    try:
        conn = sqlite3.connect(st.session_state.db_path)
        df_all = pd.read_sql_query("SELECT * FROM sales", conn)
        conn.close()

        # Parse date column
        df_all["parsed_date"] = pd.to_datetime(df_all["order_date"], errors="coerce")

        # Top dashboard filters
        st.markdown("### 🎛️ Filter Panel")
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)

        with f_col1:
            all_categories = sorted(df_all["category"].dropna().unique().tolist())
            selected_categories = st.multiselect(
                "Product Category",
                options=all_categories,
                default=all_categories,
                key="dash_filter_cat"
            )

        with f_col2:
            all_regions = sorted(df_all["region"].dropna().unique().tolist())
            selected_regions = st.multiselect(
                "Region",
                options=all_regions,
                default=all_regions,
                key="dash_filter_region"
            )

        with f_col3:
            all_payments = sorted(df_all["payment_method"].dropna().unique().tolist())
            selected_payments = st.multiselect(
                "Payment Method",
                options=all_payments,
                default=all_payments,
                key="dash_filter_payment"
            )

        with f_col4:
            min_date = df_all["parsed_date"].min().date() if df_all["parsed_date"].notna().any() else datetime.date(2023, 1, 1)
            max_date = df_all["parsed_date"].max().date() if df_all["parsed_date"].notna().any() else datetime.date(2026, 12, 31)
            selected_dates = st.date_input(
                "Order Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="dash_filter_dates"
            )

        # Apply Filters
        filtered_df = df_all[
            (df_all["category"].isin(selected_categories)) &
            (df_all["region"].isin(selected_regions)) &
            (df_all["payment_method"].isin(selected_payments))
        ]

        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_d, end_d = selected_dates
            filtered_df = filtered_df[
                (filtered_df["parsed_date"].dt.date >= start_d) &
                (filtered_df["parsed_date"].dt.date <= end_d)
            ]

        # KPIs
        st.markdown("### 📌 Performance Indicators")
        kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)

        total_sales = filtered_df["total_amount"].sum() if "total_amount" in filtered_df else 0.0
        total_txns = len(filtered_df)
        avg_ticket = total_sales / total_txns if total_txns > 0 else 0.0
        avg_profit_margin = filtered_df["profit_margin"].mean() if "profit_margin" in filtered_df else 0.0
        returns_pct = (filtered_df["returned"].eq("Yes").mean() * 100) if "returned" in filtered_df else 0.0

        with kpi_c1:
            st.metric("Total Revenue", f"₹ {total_sales:,.0f}")
        with kpi_c2:
            st.metric("Total Orders", f"{total_txns:,}")
        with kpi_c3:
            st.metric("Average Order Value", f"₹ {avg_ticket:,.0f}")
        with kpi_c4:
            st.metric("Average Profit Margin", f"{avg_profit_margin:.1f}%")
        with kpi_c5:
            st.metric("Returns Rate", f"{returns_pct:.1f}%")

        # Visualizations
        st.markdown("### 📦 Product Category & Region Breakdown")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### Revenue by Category")
            cat_sales = filtered_df.groupby("category")["total_amount"].sum().reset_index()
            st.bar_chart(cat_sales.set_index("category"), use_container_width=True)

        with c2:
            st.markdown("#### Revenue by Region")
            reg_sales = filtered_df.groupby("region")["total_amount"].sum().reset_index()
            st.bar_chart(reg_sales.set_index("region"), use_container_width=True)

        st.markdown("### 📈 Time-series & Payment Analysis")
        c3, c4 = st.columns(2)

        with c3:
            st.markdown("#### Monthly Sales Trend")
            trend_df = filtered_df.copy()
            trend_df["month"] = trend_df["parsed_date"].dt.to_period("M").astype(str)
            monthly_sales = trend_df.groupby("month")["total_amount"].sum().reset_index()
            st.line_chart(monthly_sales.set_index("month"), use_container_width=True)

        with c4:
            st.markdown("#### Payment Method Distribution")
            pay_dist = filtered_df.groupby("payment_method")["total_amount"].sum().reset_index()
            st.bar_chart(pay_dist.set_index("payment_method"), use_container_width=True)

        st.markdown("### 👥 Customer Demographics & Shipping")
        c5, c6 = st.columns(2)

        with c5:
            st.markdown("#### Customer Age Distribution")
            if "customer_age" in filtered_df and len(filtered_df) > 0:
                age_bins = [0, 25, 35, 45, 55, 100]
                age_labels = ["Under 25", "25-34", "35-44", "45-54", "55+"]
                filtered_df["age_group"] = pd.cut(filtered_df["customer_age"], bins=age_bins, labels=age_labels)
                age_dist = filtered_df["age_group"].value_counts().reindex(age_labels).reset_index()
                st.bar_chart(age_dist.set_index("age_group"), use_container_width=True)
            else:
                st.info("Age demographics not available or empty.")

        with c6:
            st.markdown("#### Delivery Times (Average Days by Region)")
            if "delivery_time_days" in filtered_df:
                del_time = filtered_df.groupby("region")["delivery_time_days"].mean().reset_index()
                st.bar_chart(del_time.set_index("region"), use_container_width=True)
            else:
                st.info("Delivery time data not available.")

        st.markdown("### 🚀 Top Selling Products")
        prod_perf = filtered_df.groupby("product_id").agg(
            total_revenue=pd.NamedAgg(column="total_amount", aggfunc="sum"),
            units_sold=pd.NamedAgg(column="quantity", aggfunc="sum"),
            average_discount=pd.NamedAgg(column="discount", aggfunc="mean"),
            average_profit=pd.NamedAgg(column="profit_margin", aggfunc="mean")
        ).sort_values(by="total_revenue", ascending=False).head(10).reset_index()

        st.dataframe(prod_perf, use_container_width=True, hide_index=True)

        # Dashboard AI Summary
        st.markdown("### 🧠 AI Executive Dashboard Summary")
        if st.button("Generate AI Summary for Filtered Data ⚡", key="gen_dash_ai"):
            with st.spinner("Analyzing dashboard metrics..."):
                try:
                    from langchain_groq import ChatGroq
                    from langchain_core.messages import HumanMessage, SystemMessage

                    top_cats = filtered_df.groupby("category")["total_amount"].sum().sort_values(ascending=False).head(3).to_string()
                    top_regs = filtered_df.groupby("region")["total_amount"].sum().sort_values(ascending=False).head(3).to_string()

                    llm = ChatGroq(
                        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                        temperature=0.3,
                        groq_api_key=os.getenv("GROQ_API_KEY")
                    )

                    system_prompt = """
You are a senior AI business intelligence analyst.
Analyze the provided filtered business metrics and summarize them concisely.
Include observations on revenue, regions, categories, and actionable recommendations.
Strictly stick to the data provided. Do not invent details.
"""

                    user_prompt = f"""
                    FILTERED BUSINESS METRICS:
                    Total Revenue: INR {total_sales:,.2f}
                    Average order value: INR {avg_ticket:,.2f}
                    Total orders: {total_txns}
                    Average Profit Margin: {avg_profit_margin:.1f}%
                    Return Rate: {returns_pct:.1f}%

                    TOP CATEGORIES:
                    {top_cats}

                    TOP REGIONS:
                    {top_regs}
                    """

                    response = llm.invoke([
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ])

                    st.success(response.content)
                except Exception as e:
                    st.error(f"AI Summary Error: {str(e)}")

    except Exception as e:
        st.error(f"Dashboard Error: {str(e)}")

# ── Tab 4: Database Inspector ─────────────────────────────────────────────────
with tab4:
    st.markdown("## 🗄️ Relational Core Explorer")

    try:
        conn = sqlite3.connect(st.session_state.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall() if t[0] != "sqlite_sequence"]

        if tables:
            st.markdown(f"**Loaded Tables in database:** `{st.session_state.db_path}`")
            selected_table = st.selectbox("Select Table to View:", options=tables, key="inspect_table_select")

            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns_info = cursor.fetchall()

            with st.expander("🛠️ Column Schema & Data Types", expanded=False):
                schema_df = pd.DataFrame(columns_info, columns=["CID", "Name", "Type", "Not Null", "Default Value", "Primary Key"])
                st.dataframe(schema_df, use_container_width=True, hide_index=True)

            # View Records with search and page size
            st.markdown("### 📑 Table Records")
            df_full = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)

            col_search, col_limit = st.columns([7, 3])
            with col_search:
                search_query = st.text_input("Search records (regex search across all fields):", value="", key="inspect_table_search")
            with col_limit:
                limit = st.selectbox("Page Size Limit:", options=[10, 25, 50, 100, 500], index=1, key="inspect_table_limit")

            if search_query.strip():
                mask = df_full.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
                df_filtered = df_full[mask]
            else:
                df_filtered = df_full

            st.write(f"Showing first {min(limit, len(df_filtered))} of {len(df_filtered)} matching records.")
            st.dataframe(df_filtered.head(limit), use_container_width=True, hide_index=True)

            # Download CSV
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data (CSV)",
                data=csv_data,
                file_name=f"{selected_table}_records.csv",
                mime="text/csv",
                key="download_inspected_data"
            )

        else:
            st.warning("No tables found in database.")
        conn.close()
    except Exception as e:
        st.error(f"Explorer Fault: {e}")

# ── Tab 5: AI Compliance & Tax Copilot ────────────────────────────────────────
with tab5:
    st.markdown("## 🧾 AI Compliance & Tax Copilot")
    st.markdown("This module analyzes your business turnover and maps it against active Indian taxation regulations to determine tax category, GST applicability, and required filing forms.")

    try:
        conn = sqlite3.connect(st.session_state.db_path)
        df_comp = pd.read_sql_query("SELECT * FROM sales", conn)
        conn.close()

        revenue_col = None
        for col in df_comp.columns:
            if any(k in col.lower() for k in ["revenue", "sales", "amount", "total", "price"]):
                revenue_col = col
                break

        if revenue_col is None:
            st.warning("⚠️ No numeric revenue/sales column detected in the active dataset. Compliance calculation cannot be finalized.")
        else:
            total_turnover = df_comp[revenue_col].sum()
            
            # Threshold gauges
            st.markdown("### 🚦 Regulatory Limits Gauge")
            gst_limit = 4000000.0
            itr4_limit = 5000000.0
            audit_limit = 50000000.0
            
            gc1, gc2, gc3 = st.columns(3)
            with gc1:
                if total_turnover > gst_limit:
                    st.markdown("""
                    <div style='background:#fef2f2; border:1px solid #000000; border-radius:0px; padding:15px; text-align:center;'>
                        <div style='font-size:0.75rem; font-family:monospace; color:#000000; font-weight:600;'>GST REGISTRATION (40L)</div>
                        <div style='font-size:1.4rem; font-weight:bold; color:#000000; margin-top:5px;'>EXCEEDED</div>
                        <div style='font-size:0.7rem; color:#7a7a7a; margin-top:5px;'>Threshold crossed. GST registration required.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='background:#ffffff; border:1px solid #000000; border-radius:0px; padding:15px; text-align:center;'>
                        <div style='font-size:0.75rem; font-family:monospace; color:#7a7a7a;'>GST REGISTRATION (40L)</div>
                        <div style='font-size:1.4rem; font-weight:bold; color:#000000; margin-top:5px;'>EXEMPT</div>
                        <div style='font-size:0.7rem; color:#7a7a7a; margin-top:5px;'>Turnover is below GST registration limits.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with gc2:
                if total_turnover <= itr4_limit:
                    st.markdown("""
                    <div style='background:#ffffff; border:1px solid #000000; border-radius:0px; padding:15px; text-align:center;'>
                        <div style='font-size:0.75rem; font-family:monospace; color:#7a7a7a;'>PRESUMPTIVE TAXATION (50L)</div>
                        <div style='font-size:1.4rem; font-weight:bold; color:#000000; margin-top:5px;'>ELIGIBLE (ITR-4)</div>
                        <div style='font-size:0.7rem; color:#7a7a7a; margin-top:5px;'>Eligible for presumptive taxation schema.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='background:#fffbeb; border:1px solid #000000; border-radius:0px; padding:15px; text-align:center;'>
                        <div style='font-size:0.75rem; font-family:monospace; color:#000000; font-weight:600;'>PRESUMPTIVE TAXATION (50L)</div>
                        <div style='font-size:1.4rem; font-weight:bold; color:#000000; margin-top:5px;'>INELIGIBLE (ITR-3)</div>
                        <div style='font-size:0.7rem; color:#7a7a7a; margin-top:5px;'>ITR-3 required due to transaction size.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with gc3:
                if total_turnover > audit_limit:
                    st.markdown("""
                    <div style='background:#fef2f2; border:1px solid #000000; border-radius:0px; padding:15px; text-align:center;'>
                        <div style='font-size:0.75rem; font-family:monospace; color:#000000; font-weight:600;'>TAX AUDIT THRESHOLD (5CR)</div>
                        <div style='font-size:1.4rem; font-weight:bold; color:#000000; margin-top:5px;'>AUDIT REQUIRED</div>
                        <div style='font-size:0.7rem; color:#7a7a7a; margin-top:5px;'>CA Audit required under Section 44AB.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='background:#ffffff; border:1px solid #000000; border-radius:0px; padding:15px; text-align:center;'>
                        <div style='font-size:0.75rem; font-family:monospace; color:#7a7a7a;'>TAX AUDIT THRESHOLD (5CR)</div>
                        <div style='font-size:1.4rem; font-weight:bold; color:#000000; margin-top:5px;'>NO AUDIT</div>
                        <div style='font-size:0.7rem; color:#7a7a7a; margin-top:5px;'>Turnover is safely below statutory audit limits.</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_met1, col_met2, col_met3 = st.columns(3)
            with col_met1:
                st.metric("Gross Turnover", f"₹ {total_turnover:,.0f}")
            with col_met2:
                if total_turnover < 4000000:
                    status_val = "Small (Micro)"
                elif total_turnover < 40000000:
                    status_val = "Medium"
                else:
                    status_val = "Large"
                st.metric("Business Classification", status_val)
            with col_met3:
                if total_turnover < 5000000:
                    itr_val = "ITR-4"
                elif total_turnover < 50000000:
                    itr_val = "ITR-3"
                else:
                    itr_val = "ITR-3 (Audit)"
                st.metric("Suggested ITR Form", itr_val)

            st.markdown("### 🤖 AI Compliance Analysis Report")
            
            from langchain_groq import ChatGroq
            from langchain_core.messages import HumanMessage, SystemMessage

            llm = ChatGroq(
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                temperature=0.2,
                groq_api_key=os.getenv("GROQ_API_KEY")
            )

            system_prompt = """
You are an Indian business taxation advisor.
Analyze the provided turnover data and generate:
1. Taxation observations
2. GST applicability observations
3. Business scale observations
4. Suggested filing guidance

Include clean visual formatting (with bullet points and headers). Do not provide legal guarantees.
"""

            user_prompt = f"""
            BUSINESS TURNOVER: {total_turnover}
            SUGGESTED ITR: {itr_val}
            GST THRESHOLD CROSSED: {total_turnover > gst_limit}
            """
            
            with st.spinner("Analyzing compliance standards..."):
                response = llm.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ])

            st.info(response.content)

    except Exception as e:
        st.error(f"Compliance Error: {str(e)}")

# ── Tab 6: Architecture Blueprint ─────────────────────────────────────────────
with tab6:
    st.markdown("## 🗺️ Multi-Agent Decision Routing Network")
    st.markdown("The system executes tasks using a LangGraph workflow that routes messages dynamically based on user intent.")
    
    st.markdown("```mermaid\n" + """
    graph TD
        START([User Input]) --> router[1. Intent Router]
        router -- Intent: compliance_audit --> audit[2. Compliance Audit Node]
        router -- Intent: sql --> schema[3. Schema Extractor]
        schema --> gen[4. SQL Generator] --> critic[5. Critic Gate] --> exec[6. DB Executor]
        exec -- Error Loop --> correction[7. Self-Healing Corrector] --> exec
        audit --> synthesis[8. NL Synthesis Engine]
        exec --> synthesis
        router -- Intent: RAG --> rag[9. Policy Lookup] --> synthesis
        synthesis --> END([Final Dashboard View Output])
        
        style START fill:#fff,stroke:#000,stroke-width:2px,color:#000
        style END fill:#fff,stroke:#000,stroke-width:2px,color:#000
        style router fill:#fff,stroke:#000,stroke-width:2px,color:#000
        style schema fill:#fff,stroke:#000,stroke-dasharray: 5 5,color:#000
        style gen fill:#fff,stroke:#000,color:#000
        style critic fill:#fff,stroke:#000,color:#000
        style exec fill:#fff,stroke:#000,color:#000
        style correction fill:#fff,stroke:#000,color:#000
        style audit fill:#fff,stroke:#000,color:#000
        style rag fill:#fff,stroke:#000,color:#000
        style synthesis fill:#fff,stroke:#000,stroke-width:2px,color:#000
    """ + "\n```")
    
    st.markdown("### ⚙️ Session States Debugger")
    
    db_size = os.path.getsize(st.session_state.db_path) if os.path.exists(st.session_state.db_path) else 0
    
    diag_col1, diag_col2 = st.columns(2)
    with diag_col1:
        st.json({
            "Active Database Path": st.session_state.db_path,
            "Database File Size (Bytes)": f"{db_size:,}",
            "Workspace State": "ACTIVE" if st.session_state.has_data else "INACTIVE",
            "Dialog History Length": len(st.session_state.history),
            "Total Session Queries Run": st.session_state.query_count,
        })
    with diag_col2:
        st.json({
            "HITL Gateway Status": "ENABLED" if hitl_enabled else "DISABLED",
            "Corporate Rules Document": "platform_rules.txt",
            "System UI Theme": "Minimalist White-and-Black Brutalist Theme",
            "Dashboard Filter Status": "CONNECTED",
        })