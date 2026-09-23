from app.llm import llm


def _format_sources(results):
    """
    Create a simple source list from retrieved policy documents.
    PyPDFLoader stores the PDF page number in metadata as a
    zero-based value, so we display it as a human-readable page.
    """

    pages = []

    for result in results:
        page_number = result.metadata.get("page")

        if page_number is not None:
            page = page_number + 1
            if page not in pages:
                pages.append(page)

    if not pages:
        return "Source: Finance Policy"

    page_text = ", ".join(
        f"Page {page}" for page in sorted(pages)
    )

    return f"Source: Finance Policy — {page_text}"


def _clean_response(response):
    """
    Remove Qwen's hidden reasoning section if it appears.
    """

    answer = response.content

    if "</think>" in answer.lower():
        answer = answer.split("</think>", 1)[-1].strip()

    return answer.strip()


def ask_rag(vector_store, query):
    """
    Answer a question using the finance policy knowledge base.
    """

    results = vector_store.similarity_search(
        query,
        k=3
    )

    context = "\n\n".join(
        result.page_content
        for result in results
    )

    prompt = f"""
You are FinGuard AI, a finance and compliance assistant.

Answer the user's question using ONLY the policy context provided below.

Instructions:
- Answer the question directly.
- Include all relevant requirements from the policy.
- Do not omit important conditions or approval requirements.
- Use clear, natural language.
- Prefer a short paragraph or bullet points when appropriate.
- Do not discuss your reasoning process.
- Do not mention the prompt, context, or retrieval process.
- If the policy does not contain enough information, say:
  "I could not find enough information in the provided policy."

Policy context:
{context}

User question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    answer = _clean_response(response)
    source = _format_sources(results)

    return f"{answer}\n\n---\n\n{source}"


def ask_invoice_compliance(vector_store, invoice_data, invoice_text):
    """
    Perform a focused compliance analysis for an invoice.
    """

    query = f"""
Review this invoice against the financial policy.

Invoice Number: {invoice_data.get("invoice_number")}
Subtotal: {invoice_data.get("subtotal")}
Tax: {invoice_data.get("tax")}
Total: {invoice_data.get("total")}

Invoice text:
{invoice_text}

Return ONLY this short format:

Policy Requirement:
[relevant requirement]

Evidence:
[evidence found in invoice]

Missing Evidence:
[important missing information]

Assessment:
Compliant / Potentially Non-Compliant / Cannot Determine

Reason:
[brief explanation]

Use only the provided policy context.
Do not invent approvals or facts.
Keep the response under 150 words.
"""

    results = vector_store.similarity_search(
        query,
        k=2
    )

    context = "\n\n".join(
        result.page_content
        for result in results
    )

    prompt = f"""
You are a financial compliance analyst.

Use ONLY the policy context below.

Give a concise answer under 150 words.
Do not provide lengthy reasoning.
Do not invent facts, approvals, or evidence.

POLICY CONTEXT:
{context}

{query}
"""

    response = llm.invoke(prompt)

    answer = _clean_response(response)
    source = _format_sources(results)

    return f"{answer}\n\n---\n\n{source}"