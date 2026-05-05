from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


@dataclass
class FeeCap:
    min_fee: Optional[Decimal] = None
    max_fee: Optional[Decimal] = None


@dataclass
class FeeResult:
    amount: Decimal
    fee_rate: Decimal
    raw_fee: Decimal
    final_fee: Decimal
    currency: str
    cap_applied: Optional[str]
    calculation_method: str


class FeeCalculator:
    def calculate(
        self,
        amount: Decimal,
        fee_rate: Decimal,
        currency: str = "RON",
        cap: Optional[FeeCap] = None,
    ) -> FeeResult:
        if amount <= Decimal("0"):
            raise ValueError("Amount must be greater than zero")

        if fee_rate < Decimal("0"):
            raise ValueError("Fee rate cannot be negative")

        raw_fee = amount * fee_rate
        final_fee = raw_fee
        cap_applied = None

        if cap:
            if cap.min_fee is not None and final_fee < cap.min_fee:
                final_fee = cap.min_fee
                cap_applied = "MIN_FEE"

            if cap.max_fee is not None and final_fee > cap.max_fee:
                final_fee = cap.max_fee
                cap_applied = "MAX_FEE"

        raw_fee = raw_fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        final_fee = final_fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        calculation_method = (
            f"fee = amount * rate = {amount} * {fee_rate} = {raw_fee} {currency}; "
            f"after caps = {final_fee} {currency}"
        )

        return FeeResult(
            amount=amount,
            fee_rate=fee_rate,
            raw_fee=raw_fee,
            final_fee=final_fee,
            currency=currency,
            cap_applied=cap_applied,
            calculation_method=calculation_method,
        )


'''
    ### Example Usage ###

calculator = FeeCalculator()

result = calculator.calculate(
    amount=Decimal("500"),
    fee_rate=Decimal("0.0185"),
    currency="RON",
    cap=FeeCap(
        min_fee=Decimal("0.10"),
        max_fee=Decimal("20.00"),
    ),
)

print(result)

'''