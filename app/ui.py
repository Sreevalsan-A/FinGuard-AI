import sys
import os
import tempfile

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import streamlit as st
from langchain_core.messages import HumanMessage

from app.supervisor import supervisor_graph, vector_store
from app.rag import ask_invoice_compliance

from app.invoice_processor import (
    extract_invoice_text,
    extract_invoice_fields,
    validate_invoice_totals,
)


st.set_page_config(
    page_title="FinGuard AI",
    page_icon="💰",
    layout="centered",
)


st.title("💰 FinGuard AI")
st.caption("Agentic AI for Finance & Compliance")


# ============================================================
# INVOICE ANALYSIS
# ============================================================

st.header("📄 Invoice Analysis")

uploaded_file = st.file_uploader(
    "Upload an invoice PDF",
    type=["pdf"],
)

if uploaded_file is not None:

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        with st.spinner("Extracting invoice information..."):
            invoice_text = extract_invoice_text(temp_path)
            invoice_data = extract_invoice_fields(invoice_text)

        st.success("Invoice processed successfully.")

        st.subheader("Extracted Invoice Details")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Invoice Number",
                invoice_data["invoice_number"] or "Not found",
            )

            st.metric(
                "Subtotal",
                (
                    f"₹{invoice_data['subtotal']:,.2f}"
                    if invoice_data["subtotal"] is not None
                    else "Not found"
                ),
            )

        with col2:
            st.metric(
                "Tax",
                (
                    f"₹{invoice_data['tax']:,.2f}"
                    if invoice_data["tax"] is not None
                    else "Not found"
                ),
            )

            st.metric(
                "Total",
                (
                    f"₹{invoice_data['total']:,.2f}"
                    if invoice_data["total"] is not None
                    else "Not found"
                ),
            )

        st.subheader("🧮 Financial Validation")

        validation = validate_invoice_totals(invoice_data)

        if validation["status"] == "Valid":
            st.success(f"✓ {validation['message']}")

        elif validation["status"] == "Mismatch":
            st.error(f"⚠ {validation['message']}")

        else:
            st.warning(validation["message"])

        if validation["expected_total"] is not None:

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Expected Total",
                    f"₹{validation['expected_total']:,.2f}",
                )

            with col2:
                st.metric(
                    "Invoice Total",
                    f"₹{invoice_data['total']:,.2f}",
                )

            with col3:
                st.metric(
                    "Tax Rate",
                    f"{validation['tax_rate']:.2f}%",
                )

        st.subheader("🛡️ Policy Compliance Analysis")

        if st.button(
            "Analyze Invoice Compliance",
            key="invoice_compliance",
        ):

            with st.spinner(
                "Reviewing invoice against financial policy..."
            ):
                compliance_result = ask_invoice_compliance(
                    vector_store,
                    invoice_data,
                    invoice_text,
                )

            st.markdown(compliance_result)

            with st.expander("🔎 Invoice Audit Trail"):

                audit_steps = [
                    "Invoice PDF uploaded.",
                    "Invoice fields extracted.",
                    "Invoice totals validated.",
                    "Relevant finance policy retrieved.",
                    "Invoice compared against policy.",
                    "Compliance assessment generated.",
                ]

                for step in audit_steps:
                    st.write(f"→ {step}")

        with st.expander("View extracted invoice text"):
            st.text(invoice_text)

    except Exception as e:
        st.error(f"Could not process the invoice: {e}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# FINguard AI CHAT
# ============================================================

st.header("💬 Ask FinGuard AI")

st.caption(
    "Ask general finance, policy, or compliance questions."
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if st.session_state.chat_history:

    st.subheader("Conversation")

    for item in st.session_state.chat_history:

        with st.chat_message("user"):
            st.write(item["question"])

        with st.chat_message("assistant"):
            st.markdown(item["answer"])

        if item.get("audit"):

            with st.expander("🔎 Audit Trail"):

                for step in item["audit"]:
                    st.write(f"→ {step}")


with st.form(
    "fin_guard_chat_form",
    clear_on_submit=True,
):

    question = st.text_area(
        "Ask a new question:",
        placeholder=(
            "Example: What approvals are required "
            "for expenses over $300 when there is "
            "no purchase order?"
        ),
        height=100,
    )

    submitted = st.form_submit_button(
        "Ask FinGuard AI"
    )


if submitted:

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner(
            "FinGuard AI is analyzing..."
        ):

            result = supervisor_graph.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content=question.strip()
                        )
                    ],
                    "audit": [],
                }
            )

        answer = result["result"]

        if "</think>" in answer.lower():
            answer = answer.split(
                "</think>",
                1,
            )[-1].strip()

        st.session_state.chat_history.append(
            {
                "question": question.strip(),
                "answer": answer,
                "audit": result.get("audit", []),
            }
        )

        st.rerun()