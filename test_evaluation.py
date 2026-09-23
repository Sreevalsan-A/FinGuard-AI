from app.finance_tools import (
    calculate_invoice_total,
    calculate_variance,
    check_budget_status,
    detect_duplicate_invoice,
)

from app.invoice_processor import (
    extract_invoice_fields,
    validate_invoice_totals,
)


def test_invoice_field_extraction():

    text = """
    SAMPLE INVOICE

    Invoice Number: INV-1001

    Subtotal: 10,000.00
    GST: 1,800.00
    Grand Total: 11,800.00
    """

    result = extract_invoice_fields(text)

    assert result["invoice_number"] == "INV-1001"
    assert result["subtotal"] == 10000.00
    assert result["tax"] == 1800.00
    assert result["total"] == 11800.00


def test_invoice_total_validation():

    invoice = {
        "subtotal": 10000.00,
        "tax": 1800.00,
        "total": 11800.00,
    }

    result = validate_invoice_totals(invoice)

    assert result["status"] == "Valid"
    assert result["expected_total"] == 11800.00
    assert result["difference"] == 0.00
    assert result["tax_rate"] == 18.00


def test_invoice_mismatch_detection():

    invoice = {
        "subtotal": 10000.00,
        "tax": 1800.00,
        "total": 12000.00,
    }

    result = validate_invoice_totals(invoice)

    assert result["status"] == "Mismatch"
    assert result["difference"] == 200.00


def test_invoice_total_tool():

    result = calculate_invoice_total.invoke(
        {
            "subtotal": 10000,
            "tax_rate": 18
        }
    )

    assert result["tax"] == 1800.00
    assert result["total"] == 11800.00


def test_variance_tool():

    result = calculate_variance.invoke(
        {
            "budget": 10000,
            "actual": 8500
        }
    )

    assert result["variance"] == 1500.00


def test_budget_status():

    within_budget = check_budget_status.invoke(
        {
            "budget": 10000,
            "actual": 8500
        }
    )

    over_budget = check_budget_status.invoke(
        {
            "budget": 10000,
            "actual": 12000
        }
    )

    assert within_budget["status"] == "Within budget"
    assert over_budget["status"] == "Over budget"


def test_duplicate_invoice_detection():

    result = detect_duplicate_invoice.invoke(
        {
            "invoice_numbers": [
                "INV-1001",
                "INV-1002",
                "INV-1001",
            ]
        }
    )

    assert result["has_duplicates"] is True
    assert "INV-1001" in result["duplicates"]


def test_no_duplicate_invoice():

    result = detect_duplicate_invoice.invoke(
        {
            "invoice_numbers": [
                "INV-1001",
                "INV-1002",
                "INV-1003",
            ]
        }
    )

    assert result["has_duplicates"] is False
    assert result["duplicates"] == []


if __name__ == "__main__":

    tests = [
        test_invoice_field_extraction,
        test_invoice_total_validation,
        test_invoice_mismatch_detection,
        test_invoice_total_tool,
        test_variance_tool,
        test_budget_status,
        test_duplicate_invoice_detection,
        test_no_duplicate_invoice,
    ]

    passed = 0

    print("\nFinGuard AI Evaluation Suite")
    print("=" * 40)

    for test in tests:

        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1

        except Exception as e:
            print(f"FAIL: {test.__name__}")
            print(f"      {e}")

    print("=" * 40)
    print(
        f"Result: {passed}/{len(tests)} tests passed."
    )

    if passed != len(tests):
        raise SystemExit(1)

    print("All deterministic evaluations passed.")