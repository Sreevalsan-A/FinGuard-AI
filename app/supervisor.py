import os
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from app.llm import llm
from app.graph import finance_graph
from app.document_loader import load_finance_document
from app.text_splitter import split_documents
from app.vector_store import create_vector_store, load_vector_store
from app.rag import ask_rag


class SupervisorState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    route: str
    result: str
    audit: list[str]


if os.path.exists("data/vectorstore/index.faiss"):
    vector_store = load_vector_store()
else:
    documents = load_finance_document()
    chunks = split_documents(documents)
    vector_store = create_vector_store(chunks)


def add_audit(state: SupervisorState, message: str):
    existing = state.get("audit", [])
    return existing + [message]


def supervisor(state: SupervisorState):
    question = state["messages"][-1].content

    prompt = f"""
You are the routing supervisor for FinGuard AI.

Choose exactly ONE destination for the user's question.

FINANCE
Use when the user needs a calculation or financial tool.

RAG
Use when the user asks about information contained in
the financial policy documents.

COMPLIANCE
Use when the user asks whether an action or situation
complies with a financial policy.

Examples:

Question: Calculate an invoice total of 10000 with 18% tax.
Answer: FINANCE

Question: What should an organization include in its financial policies?
Answer: RAG

Question: What does the policy say about expense procedures?
Answer: RAG

Question: An employee purchased something without approval.
Is this compliant with the policy?
Answer: COMPLIANCE

Return ONLY the destination name.

User question:
{question}

Destination:
"""

    response = llm.invoke(prompt)

    raw = response.content.strip()

    if "</think>" in raw.lower():
        raw = raw.lower().split("</think>")[-1].strip()

    raw = raw.upper()

    if raw.endswith("FINANCE"):
        route = "FINANCE"
    elif raw.endswith("COMPLIANCE"):
        route = "COMPLIANCE"
    elif raw.endswith("RAG"):
        route = "RAG"
    else:
        route = "RAG"

    audit = add_audit(
        state,
        f"Supervisor selected {route} route."
    )

    return {
        "route": route,
        "audit": audit
    }


def finance_node(state: SupervisorState):
    result = finance_graph.invoke(
        {
            "messages": state["messages"]
        }
    )

    audit = add_audit(
        state,
        "Finance agent executed finance tools."
    )

    audit = add_audit(
        {
            **state,
            "audit": audit
        },
        "Finance agent returned a result."
    )

    return {
        "result": result["messages"][-1].content,
        "audit": audit
    }


def rag_node(state: SupervisorState):
    question = state["messages"][-1].content

    audit = add_audit(
        state,
        "RAG agent searched the finance policy knowledge base."
    )

    answer = ask_rag(
        vector_store,
        question
    )

    audit = add_audit(
        {
            **state,
            "audit": audit
        },
        "RAG agent generated the policy-based answer."
    )

    return {
        "result": answer,
        "audit": audit
    }


def compliance_node(state: SupervisorState):
    question = state["messages"][-1].content

    audit = add_audit(
        state,
        "Compliance agent searched the finance policy knowledge base."
    )

    answer = ask_rag(
        vector_store,
        f"""
You are a financial compliance analyst.

Review the user's situation against the financial policy
provided in the document.

Question:
{question}

Provide your assessment using this structure:

Compliance Status:
Compliant / Potentially Non-Compliant / Cannot Determine

Relevant Policy:
Explain the relevant policy requirement from the document.

Assessment:
Explain how the situation relates to the policy.

Recommendation:
Suggest the appropriate next step.

Use only information supported by the provided document.

If the document does not provide enough information,
say "Cannot Determine".
"""
    )

    audit = add_audit(
        {
            **state,
            "audit": audit
        },
        "Compliance agent generated the policy-based assessment."
    )

    return {
        "result": answer,
        "audit": audit
    }


def route_question(state: SupervisorState):
    return state["route"]


graph_builder = StateGraph(SupervisorState)

graph_builder.add_node(
    "supervisor",
    supervisor
)

graph_builder.add_node(
    "finance",
    finance_node
)

graph_builder.add_node(
    "rag",
    rag_node
)

graph_builder.add_node(
    "compliance",
    compliance_node
)

graph_builder.add_edge(
    START,
    "supervisor"
)

graph_builder.add_conditional_edges(
    "supervisor",
    route_question,
    {
        "FINANCE": "finance",
        "RAG": "rag",
        "COMPLIANCE": "compliance",
    }
)

graph_builder.add_edge(
    "finance",
    END
)

graph_builder.add_edge(
    "rag",
    END
)

graph_builder.add_edge(
    "compliance",
    END
)

supervisor_graph = graph_builder.compile()