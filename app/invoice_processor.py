import re

from langchain_community.document_loaders import PyPDFLoader


def extract_invoice_text(pdf_path: str) -> str:
    """
    Extract text from an uploaded invoice PDF.
    """

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text = "\n".join(
        document.page_content
        for document in documents
    )

    return text


def _extract_amount(pattern: str, text: str):
    """
    Extract a numeric amount from invoice text.
    """

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    value = match.group(1)

    return float(
        value.replace(",", "")
    )


def extract_invoice_fields(text: str) -> dict:
    """
    Extract basic invoice fields from invoice text.
    """

    # Invoice number
    invoice_match = re.search(
        r"\binvoice\s+(?:number|no\.?|#)\s*[:.-]?\s*([A-Z0-9][A-Z0-9-]*)",
        text,
        re.IGNORECASE
    )

    invoice_number = None

    if invoice_match:
        invoice_number = invoice_match.group(1).strip()


    # Subtotal
    subtotal = _extract_amount(
        r"\bsub[-\s]?total\b\s*[:\-]?\s*[^0-9\s]*\s*([\d,]+(?:\.\d{1,2})?)",
        text
    )


    # Tax / GST / VAT
    tax = _extract_amount(
        r"\b(?:tax|gst|vat)\b\s*[:\-]?\s*[^0-9\s]*\s*([\d,]+(?:\.\d{1,2})?)",
        text
    )


    # Total
    total = _extract_amount(
        r"\b(?:grand\s+total|total\s+amount|total)\b\s*[:\-]?\s*[^0-9\s]*\s*([\d,]+(?:\.\d{1,2})?)",
        text
    )


    return {
        "invoice_number": invoice_number,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "raw_text": text
    }


def validate_invoice_totals(invoice_data: dict) -> dict:
    """
    Validate the mathematical consistency of an invoice.

    Expected total = subtotal + tax.
    """

    subtotal = invoice_data.get("subtotal")
    tax = invoice_data.get("tax")
    total = invoice_data.get("total")

    if (
        subtotal is None
        or tax is None
        or total is None
    ):
        return {
            "status": "Cannot Determine",
            "expected_total": None,
            "difference": None,
            "tax_rate": None,
            "message": "Required financial fields are missing."
        }


    expected_total = round(
        subtotal + tax,
        2
    )


    difference = round(
        total - expected_total,
        2
    )


    tax_rate = (
        round(
            (tax / subtotal) * 100,
            2
        )
        if subtotal != 0
        else None
    )


    if abs(difference) < 0.01:

        status = "Valid"

        message = (
            "Invoice total matches subtotal plus tax."
        )

    else:

        status = "Mismatch"

        message = (
            "Invoice total does not match "
            "subtotal plus tax."
        )


    return {
        "status": status,
        "expected_total": expected_total,
        "difference": difference,
        "tax_rate": tax_rate,
        "message": message
    }