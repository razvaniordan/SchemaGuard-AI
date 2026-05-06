from decimal import Decimal
from fee_calculator import FeeCalculator, FeeCap


def test_basic_fee_calculation():
    calculator = FeeCalculator()

    result = calculator.calculate(
        amount=Decimal("500"),
        fee_rate=Decimal("0.0185"),
        currency="RON"
    )

    assert result.raw_fee == Decimal("9.25")
    assert result.final_fee == Decimal("9.25")


def test_fee_with_caps():
    calculator = FeeCalculator()

    result = calculator.calculate(
        amount=Decimal("100"),
        fee_rate=Decimal("0.05"),  # 5%
        currency="RON",
        cap=FeeCap(min_fee=Decimal("10"), max_fee=Decimal("20"))
    )

    # raw = 5 → sub min → devine 10
    assert result.final_fee == Decimal("10.00")
    assert result.cap_applied == "MIN_FEE"


def test_ron_to_eur_conversion():
    calculator = FeeCalculator()

    result = calculator.calculate(
        amount=Decimal("500"),
        fee_rate=Decimal("0.02"),
        currency="RON"
    )

    # 500 * 0.02 = 10 RON → 2 EUR
    assert result.final_fee == Decimal("10.00")
    assert result.final_fee_eur == Decimal("2.00")


def test_bankers_rounding():
    calculator = FeeCalculator()

    result = calculator.calculate(
        amount=Decimal("100.05"),
        fee_rate=Decimal("0.01"),
        currency="EUR"
    )

    # verificăm că nu crapă și că e rotunjit corect
    assert result.final_fee is not None