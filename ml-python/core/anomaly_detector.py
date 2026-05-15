from datetime import datetime
from statistics import mean, stdev
from typing import Any, List

from models.analysis_models import (
    AnomalyDetectionResponse,
    RuleEngineResult,
    TransactionAnomaly,
)


class AnomalyDetector:
    def detect(
        self,
        results: List[RuleEngineResult],
    ) -> AnomalyDetectionResponse:
        """
        Detect abnormal transactions across a portfolio.

        Business rules are intentionally explicit and explainable:
        - Fee outlier detection
        - Category mismatch detection
        - Missing 3DS detection for e-commerce transactions
        - Late clearing detection
        """

        anomalies = []
        warnings = []

        if not results:
            return AnomalyDetectionResponse(
                anomalies=[],
                warnings=["No transactions provided for anomaly detection."],
            )

        anomalies.extend(self._detect_fee_outliers(results, warnings))
        anomalies.extend(self._detect_category_mismatches(results, warnings))
        anomalies.extend(self._detect_missing_3ds(results, warnings))
        anomalies.extend(self._detect_timing_anomalies(results, warnings))

        return AnomalyDetectionResponse(
            anomalies=anomalies,
            warnings=warnings,
        )

    def _detect_fee_outliers(
        self,
        results: List[RuleEngineResult],
        warnings: List[str],
    ) -> List[TransactionAnomaly]:
        """
        Detect transactions where the fee rate is unusually high.
        """

        anomalies = []
        fee_rates = [result.feeRate for result in results if result.feeRate is not None]

        if not fee_rates:
            warnings.append("Fee outlier check skipped because no fee rates were provided.")
            return anomalies

        if len(fee_rates) < 3:
            threshold = 2.0

            for result in results:
                if result.feeRate > threshold:
                    anomalies.append(
                        self._build_anomaly(
                            result=result,
                            anomaly_type="FEE_OUTLIER",
                            expected_fee=threshold,
                            actual_fee=result.feeRate,
                            explanation="Fee rate is above the fallback threshold for small datasets.",
                        )
                    )

            return anomalies

        average_fee = mean(fee_rates)
        fee_std_dev = stdev(fee_rates)
        threshold = average_fee + (2 * fee_std_dev)

        for result in results:
            if result.feeRate > threshold:
                anomalies.append(
                    self._build_anomaly(
                        result=result,
                        anomaly_type="FEE_OUTLIER",
                        expected_fee=round(threshold, 4),
                        actual_fee=result.feeRate,
                        explanation="Fee rate is significantly higher than the portfolio average.",
                    )
                )

        return anomalies

    def _detect_category_mismatches(
        self,
        results: List[RuleEngineResult],
        warnings: List[str],
    ) -> List[TransactionAnomaly]:
        """
        Detect unusual combinations between transaction data and category.
        """

        anomalies = []

        for result in results:
            transaction = result.transaction

            if "threeDS" not in transaction:
                warnings.append(
                    "Category mismatch check skipped for transaction missing threeDS."
                )
                continue

            three_ds_enabled = self._is_three_ds_enabled(transaction.get("threeDS"))
            category = str(result.category or "").lower()

            if three_ds_enabled and "non-secure" in category:
                anomalies.append(
                    self._build_anomaly(
                        result=result,
                        anomaly_type="CATEGORY_MISMATCH",
                        expected_fee=None,
                        actual_fee=result.feeRate,
                        explanation="Transaction has 3DS enabled but is classified as non-secure.",
                    )
                )

            if not three_ds_enabled and "secure" in category and "non-secure" not in category:
                anomalies.append(
                    self._build_anomaly(
                        result=result,
                        anomaly_type="CATEGORY_MISMATCH",
                        expected_fee=None,
                        actual_fee=result.feeRate,
                        explanation="Transaction is not 3DS authenticated but is classified as secure.",
                    )
                )

        return anomalies

    def _detect_missing_3ds(
        self,
        results: List[RuleEngineResult],
        warnings: List[str],
    ) -> List[TransactionAnomaly]:
        """
        Detect e-commerce transactions that are not 3DS authenticated.
        """

        anomalies = []

        for result in results:
            transaction = result.transaction
            channel = self._normalize_channel(
                transaction.get("paymentChannel") or transaction.get("channel")
            )

            if channel != "ecommerce":
                continue

            if "threeDS" not in transaction:
                warnings.append(
                    "Missing 3DS check skipped for e-commerce transaction missing threeDS."
                )
                continue

            if self._is_three_ds_enabled(transaction.get("threeDS")):
                continue

            amount = self._as_float(transaction.get("amount"), 0.0)

            anomalies.append(
                self._build_anomaly(
                    result=result,
                    anomaly_type="MISSING_3DS",
                    expected_fee=None,
                    actual_fee=result.feeAmount,
                    deviation=amount,
                    explanation=(
                        "E-commerce transaction is missing 3DS authentication and may "
                        "qualify for worse interchange fees."
                    ),
                )
            )

        return anomalies

    def _detect_timing_anomalies(
        self,
        results: List[RuleEngineResult],
        warnings: List[str],
    ) -> List[TransactionAnomaly]:
        """
        Detect authorization-to-clearing delays.

        Business rule:
        - 2 days is a medium-risk signal.
        - 3 or more days is a high-risk signal.
        """

        anomalies = []

        for result in results:
            transaction = result.transaction
            delay_days = self._get_clearing_delay_days(transaction)

            if delay_days is None:
                warnings.append(
                    "Timing anomaly check skipped for transaction missing or invalid clearing delay data."
                )
                continue

            if delay_days < 2:
                continue

            anomalies.append(
                self._build_anomaly(
                    result=result,
                    anomaly_type="LATE_CLEARING",
                    expected_fee=None,
                    actual_fee=result.feeAmount,
                    deviation=float(delay_days),
                    explanation=(
                        f"Clearing delay is {delay_days} days, which may prevent "
                        "optimal fee qualification."
                    ),
                )
            )

        return anomalies

    def _build_anomaly(
        self,
        result: RuleEngineResult,
        anomaly_type: str,
        expected_fee: float | None,
        actual_fee: float | None,
        explanation: str,
        deviation: float | None = None,
    ) -> TransactionAnomaly:
        transaction = result.transaction
        transaction_id = transaction.get("transactionId")

        if deviation is None and expected_fee is not None and actual_fee is not None:
            deviation = round(actual_fee - expected_fee, 4)

        severity = self._calculate_severity(
            anomaly_type=anomaly_type,
            deviation=deviation,
            transaction=transaction,
        )

        return TransactionAnomaly(
            transactionId=str(transaction_id) if transaction_id is not None else None,
            anomalyType=anomaly_type,
            expectedFee=expected_fee,
            actualFee=actual_fee,
            deviation=deviation,
            severity=severity,
            explanation=explanation,
        )

    def _calculate_severity(
        self,
        anomaly_type: str,
        deviation: float | None,
        transaction: dict[str, Any],
    ) -> str:
        if anomaly_type == "MISSING_3DS":
            amount = self._as_float(transaction.get("amount"), 0.0)

            if amount >= 5000:
                return "HIGH"

            if amount >= 500:
                return "MEDIUM"

            return "LOW"

        if anomaly_type == "LATE_CLEARING":
            delay_days = deviation or 0

            if delay_days >= 3:
                return "HIGH"

            if delay_days >= 2:
                return "MEDIUM"

            return "LOW"

        if deviation is None:
            return "MEDIUM"

        absolute_deviation = abs(float(deviation))

        if absolute_deviation >= 50:
            return "HIGH"

        if absolute_deviation >= 5:
            return "MEDIUM"

        return "LOW"

    def _get_clearing_delay_days(self, transaction: dict[str, Any]) -> int | None:
        existing_value = transaction.get("clearingDelayDays")

        if existing_value is not None:
            try:
                return max(int(existing_value), 0)
            except (TypeError, ValueError):
                return None

        auth_date = transaction.get("authDate")
        clearing_date = transaction.get("clearingDate")

        if not auth_date or not clearing_date:
            return None

        try:
            auth_dt = datetime.fromisoformat(str(auth_date))
            clearing_dt = datetime.fromisoformat(str(clearing_date))
        except ValueError:
            return None

        return max((clearing_dt - auth_dt).days, 0)

    def _normalize_channel(self, value: Any) -> str:
        normalized = str(value or "").replace("_", "").replace("-", "").lower()

        if normalized in {"ecommerce", "ecom", "cardnotpresent", "cnp"}:
            return "ecommerce"

        return normalized

    def _is_three_ds_enabled(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value

        normalized = str(value or "").strip().lower()
        return normalized in {"true", "yes", "y", "1", "enabled"}

    def _as_float(self, value: Any, fallback: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback
