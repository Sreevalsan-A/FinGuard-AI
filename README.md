# FinGuard AI

An Agentic AI assistant for Finance and Compliance workflows, built using LangGraph, RAG, FAISS, Ollama, and Qwen3.

FinGuard AI combines deterministic financial tools, document intelligence, retrieval-augmented generation, and agentic workflow orchestration to help analyze financial documents and answer finance and compliance questions.

---

## 🚀 Key Features

- 🤖 Agentic AI workflow using LangGraph
- 🧭 Supervisor-based intelligent routing
- 📚 Retrieval-Augmented Generation (RAG)
- 📄 Finance policy document analysis
- 🧮 Deterministic financial calculation tools
- 🧾 Invoice PDF extraction and validation
- 🛡️ Invoice compliance analysis
- 🔎 Policy source/page references
- 📋 Agent audit trail
- 💬 Conversational AI interface
- 🧪 Automated evaluation tests

---

## 🏗️ Architecture

```text
                         User
                           │
                           ▼
                    Streamlit UI
                           │
                           ▼
                  LangGraph Supervisor
                    /        |        \
                   /         |         \
                  ▼          ▼          ▼
             Finance       RAG      Compliance
              Agent       Agent        Agent
                │           │            │
                ▼           ▼            ▼
          Finance Tools   FAISS      Policy Retrieval
                            │            │
                            └──────┬─────┘
                                   ▼
                                Qwen3

The supervisor determines which specialized workflow should handle the user's request.

🧠 RAG Pipeline
Finance Policy PDF
        │
        ▼
   PDF Extraction
        │
        ▼
    Text Chunking
        │
        ▼
 HuggingFace Embeddings
        │
        ▼
      FAISS
        │
        ▼
Relevant Policy Context
        │
        ▼
      Qwen3
        │
        ▼
     Final Answer

The system retrieves relevant sections of the finance policy before generating an answer.

Policy responses include the relevant document pages used as supporting evidence.

🧾 Invoice Intelligence

FinGuard AI can process uploaded invoice PDFs and extract:

Invoice number
Subtotal
Tax
Total amount

It also performs deterministic financial validation:

Subtotal + Tax = Invoice Total

The system calculates:

Expected invoice total
Difference between expected and actual total
Effective tax rate
Invoice validation status

After validation, the invoice can be reviewed against the finance policy for compliance.

🛡️ Compliance Analysis

The compliance workflow:

Retrieves relevant finance policy information.
Identifies the applicable policy requirement.
Compares the available evidence against the requirement.
Determines whether the situation is:
Compliant
Potentially Non-Compliant
Cannot Determine
Provides a recommended next step.
Displays supporting policy pages.

The system is designed to avoid inventing approvals, evidence, or policy requirements that are not present in the source document.

🧮 Finance Tools

FinGuard AI includes deterministic Python tools for:

Invoice Calculation

Calculates:

Tax = Subtotal × Tax Rate
Total = Subtotal + Tax
Budget Variance

Calculates the difference between budget and actual spending.

Budget Status

Determines whether spending is within or over the allocated budget.

Duplicate Invoice Detection

Identifies duplicate invoice numbers.

These calculations are performed by Python tools rather than relying on the LLM for arithmetic.

🔎 Evidence & Sources

Policy-based responses provide source information such as:

Source: Finance Policy — Page 14, Page 15

This makes the generated responses more traceable and useful for compliance workflows.

📋 Audit Trail

FinGuard AI records the major steps performed during an interaction.

Example:

→ Supervisor selected COMPLIANCE route.
→ Compliance agent searched the finance policy knowledge base.
→ Compliance agent generated the policy-based assessment.

For invoice analysis, the audit trail includes steps such as:

→ Invoice PDF uploaded.
→ Invoice fields extracted.
→ Invoice totals validated.
→ Relevant finance policy retrieved.
→ Invoice compared against policy.
→ Compliance assessment generated.
💬 Conversational AI

The Streamlit interface supports conversational finance and compliance questions.

Example:

User:
What approvals are required for expenses over $300
when there is no purchase order?

FinGuard AI:
Provides the relevant policy requirements
with supporting policy pages.

Users can continue asking new questions while previous conversation results remain visible.

🧪 Evaluation

The project includes a deterministic evaluation suite covering:

Invoice field extraction
Invoice total validation
Invoice mismatch detection
Invoice calculation
Budget variance
Budget status
Duplicate invoice detection

Run the evaluation with:

python test_evaluation.py

Current deterministic evaluation:

8/8 tests passed
All deterministic evaluations passed.
📁 Project Structure
FinGuard-AI/
│
├── app/
│   ├── __init__.py
│   ├── llm.py
│   ├── document_loader.py
│   ├── text_splitter.py
│   ├── vector_store.py
│   ├── rag.py
│   ├── finance_tools.py
│   ├── graph.py
│   ├── supervisor.py
│   ├── ui.py
│   └── invoice_processor.py
│
├── data/
│   ├── documents/
│   │   └── finance_policy.pdf
│   │
│   └── vectorstore/
│       ├── index.faiss
│       └── index.pkl
│
├── test_evaluation.py
├── main.py
├── README.md
└── requirements.txt
🛠️ Technology Stack
Python
LangChain
LangGraph
Ollama
Qwen3
Hugging Face Embeddings
FAISS
PyPDF
PyTorch
Streamlit
Pydantic
⚙️ Installation
1. Clone the repository
git clone <your-repository-url>
cd FinGuard-AI
2. Create a virtual environment
python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Install the Qwen model

Make sure Ollama is installed and run:

ollama pull qwen3:4b

Verify:

ollama list
▶️ Run the Application

From the project root:

streamlit run app\ui.py

The Streamlit interface will open in your browser.

🧪 Run Tests

Run the deterministic evaluation suite:

python test_evaluation.py

Expected result:

FinGuard AI Evaluation Suite
========================================
PASS: test_invoice_field_extraction
PASS: test_invoice_total_validation
PASS: test_invoice_mismatch_detection
PASS: test_invoice_total_tool
PASS: test_variance_tool
PASS: test_budget_status
PASS: test_duplicate_invoice_detection
PASS: test_no_duplicate_invoice
========================================
Result: 8/8 tests passed.
All deterministic evaluations passed.
⚡ Design Considerations
Deterministic Financial Calculations

Financial calculations are handled through Python tools instead of relying on LLM-generated arithmetic.

Retrieval-Grounded Responses

Policy questions are answered using retrieved document context rather than relying only on the model's general knowledge.

Agentic Routing

The LangGraph supervisor routes requests to specialized workflows based on the user's intent.

Traceability

Policy responses include supporting source pages, while agent workflows expose an audit trail.

Modular Architecture

The application separates:

LLM configuration
Document ingestion
Text splitting
Vector storage
RAG
Financial tools
Agent graphs
Invoice processing
User interface

This makes the system easier to extend and maintain.

🚧 Future Improvements

Possible future enhancements include:

Multi-document knowledge bases
Database integration
More advanced invoice extraction
Authentication and role-based access
Human approval workflows
API layer using FastAPI
Docker deployment
Cloud deployment
Improved evaluation of LLM-generated responses
Additional finance and compliance agents
🎯 Project Goal

FinGuard AI demonstrates how modern Generative AI and Agentic AI techniques can be combined with deterministic business logic and document retrieval to build a practical finance and compliance application.

The project focuses on combining:

Generative AI
     +
RAG
     +
Agentic Workflows
     +
Deterministic Tools
     +
Document Intelligence
     +
Compliance

into a single end-to-end application.