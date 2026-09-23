from langchain_core.tools import tool


@tool
def calculate_invoice_total(subtotal: float, tax_rate: float):
    """Calculate tax and total amount for an invoice."""
    tax = subtotal * (tax_rate / 100)
    total = subtotal + tax

    return {
        "subtotal": subtotal,
        "tax": round(tax, 2),
        "total": round(total, 2)
    }


@tool
def calculate_variance(budget: float, actual: float):
    """Calculate the difference between budget and actual spending."""
    variance = budget - actual

    return {
        "budget": budget,
        "actual": actual,
        "variance": round(variance, 2)
    }


@tool
def check_budget_status(budget: float, actual: float):
    """Check whether actual spending is within the budget."""
    if actual <= budget:
        status = "Within budget"
    else:
        status = "Over budget"

    return {
        "budget": budget,
        "actual": actual,
        "status": status
    }


@tool
def detect_duplicate_invoice(invoice_numbers: list[str]):
    """Detect duplicate invoice numbers."""
    seen = set()
    duplicates = []

    for invoice in invoice_numbers:
        if invoice in seen:
            duplicates.append(invoice)
        else:
            seen.add(invoice)

    return {
        "duplicates": duplicates,
        "has_duplicates": len(duplicates) > 0
    }