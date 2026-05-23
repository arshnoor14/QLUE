# Qlue: Enterprise Data Intelligence & Compliance Workspace

## Overview
Qlue is a minimalist technology workspace interface engineered for autonomous data analysis, natural language SQL generation, and automated compliance auditing. Utilizing a brutalist architectural design and strict API state management, the system enables users to query proprietary datasets—uploaded via CSV or Excel—using conversational English. 

The backend is driven by a LangGraph multi-agent routing network and the Groq LLM API, ensuring dynamic intent classification, self-healing query execution, and accurate policy retrieval.

## Core Features

* **Intelligent Intent Routing:** The system categorizes user queries into distinct execution paths (SQL generation, Regulatory Audit, RAG Policy Lookup, or General Dialogue) to optimize response accuracy.
* **Autonomous Text-to-SQL Engine:** Converts natural language into valid SQLite syntax. The engine incorporates a "Critic Gate" for schema validation and a self-healing loop that automatically corrects execution errors.
* **Automated Business Intelligence (BI):** Dynamically generates interactive dashboards, key performance indicators (KPIs), and executive summaries upon dataset initialization.
* **Tax & Compliance Copilot:** Analyzes aggregate financial metrics against Indian taxation frameworks to recommend appropriate Income Tax Return (ITR) forms, assess GST registration thresholds, and flag statutory audit requirements.
* **Human-in-the-Loop (HITL) Gateway:** A configurable security protocol that pauses execution, allowing administrators to review and authorize AI-generated SQL schemas prior to database execution.

## System Architecture

The backend operates on a state machine architecture defined in `agent.py`. The execution flow proceeds as follows:
1. **Intent Router:** Classifies the query based on predefined logic.
2. **Schema Extractor:** Dynamically maps the uploaded dataset structure.
3. **SQL Generator & Critic:** Formulates and reviews the SQL statement for syntactic and structural validity.
4. **Execution & Correction Node:** Executes the query against the SQLite database, with automated retries up to a specified limit if an error occurs.
5. **Synthesis Engine:** Translates raw database outputs into professional, human-readable insights.

## Prerequisites

Ensure the following dependencies are installed in your environment:
* Python 3.9+
* Required Python packages as specified in the dependencies list.

## Installation & Deployment

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/your-organization/qlue.git](https://github.com/your-organization/qlue.git)
   cd qlue
