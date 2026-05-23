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


<img width="1906" height="874" alt="image" src="https://github.com/user-attachments/assets/2b5a49bf-2835-43b5-97a2-559230cd86f0" />
<img width="1905" height="871" alt="image" src="https://github.com/user-attachments/assets/62062430-5e9d-42f8-8ff4-15ce699f2675" />
<img width="1914" height="748" alt="image" src="https://github.com/user-attachments/assets/524e34cd-1590-455f-9638-e4f09b5c5e63" />
<img width="1919" height="653" alt="image" src="https://github.com/user-attachments/assets/47680526-efad-4c46-b581-51b832612346" />
<img width="1919" height="877" alt="image" src="https://github.com/user-attachments/assets/5f4f22bc-0641-4e78-9e9e-232376079fcc" />
<img width="1919" height="761" alt="image" src="https://github.com/user-attachments/assets/dd8de1e7-5440-4aae-8627-a0958fe840be" />
<img width="1919" height="814" alt="image" src="https://github.com/user-attachments/assets/6a401976-6e73-4fd0-9dd9-c52c1a7b8ad4" />
<img width="1913" height="766" alt="image" src="https://github.com/user-attachments/assets/8386981e-21b0-4a08-bd2a-212a1cb30f3c" />


<img width="1905" height="868" alt="image" src="https://github.com/user-attachments/assets/a24c9a3c-dfc3-4c46-9720-0d5f39ca5523" />
<img width="1919" height="787" alt="image" src="https://github.com/user-attachments/assets/e7082ed6-578c-4860-b41a-210a1051a899" />

