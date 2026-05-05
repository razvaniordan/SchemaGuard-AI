from datetime import datetime
from statistics import mean, stdev
from typing import List

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

        Phase 1 uses heuristic and statistical rules:
        - Fee outlier detection
        - Category mismatch detection
        - Timing anomaly detection

        Later this can evolve into Isolation Forest or One-Class SVM.
        """

        # Store all anomalies detected across transactions
        anomalies = []

        # Store warnings for skipped checks or incomplete data
        warnings = []

        # If no transactions are provided, return an empty response
        if not results:
            return AnomalyDetectionResponse(
                anomalies=[],
                warnings=["No transactions provided for anomaly detection."],
            )

        # Run each anomaly check separately
        anomalies.extend(self._detect_fee_outliers(results, warnings))
        anomalies.extend(self._detect_category_mismatches(results, warnings))
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

        For larger datasets:
        - Use z-score style rule: feeRate > mean + 2 * std

        For small datasets:
        - Fall back to simple threshold rule.
        """

        anomalies = []

        # Extract valid fee rates
        fee_rates = [
            result.feeRate
            for result in results
            if result.feeRate is not None
        ]

        # If no valid fee rates exist, skip this check
        if not fee_rates:
            warnings.append("Fee outlier check skipped because no fee rates were provided.")
            return anomalies

        # Small dataset fallback
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

        # Statistical threshold for larger datasets
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

        Example:
        - threeDS=True but category still says Non-Secure
        """

        anomalies = []

        for result in results:
            transaction = result.transaction

            # Skip if required field is missing
            if "threeDS" not in transaction:
                warnings.append("Category mismatch check skipped for transaction missing threeDS.")
                continue

            three_ds_enabled = transaction.get("threeDS")
            category = result.category.lower()

            # If 3DS is enabled but category says non-secure, this is suspicious
            if three_ds_enabled is True and "non-secure" in category:
                anomalies.append(
                    self._build_anomaly(
                        result=result,
                        anomaly_type="CATEGORY_MISMATCH",
                        expected_fee=None,
                        actual_fee=result.feeRate,
                        explanation=(
                            "Transaction has 3DS enabled but is classified as non-secure."
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
        Detect extreme authorization-to-clearing delays.

        Phase 1 rule:
        - Clearing delay above 3 days is treated as abnormal.
        """

        anomalies = []

        for result in results:
            transaction = result.transaction

            auth_date = transaction.get("authDate")
            clearing_date = transaction.get("clearingDate")

            # Skip if either date is missing
            if not auth_date or not clearing_date:
                warnings.append(
                    "Timing anomaly check skipped for transaction missing authDate or clearingDate."
                )
                continue

            try:
                auth_dt = datetime.fromisoformat(auth_date)
                clearing_dt = datetime.fromisoformat(clearing_date)
            except ValueError:
                warnings.append(
                    "Timing anomaly check skipped because dates were not valid ISO format."
                )
                continue

            delay_days = (clearing_dt - auth_dt).days

            # Extreme clearing delay rule
            if delay_days > 3:
                anomalies.append(
                    self._build_anomaly(
                        result=result,
                        anomaly_type="TIMING_ANOMALY",
                        expected_fee=None,
                        actual_fee=result.feeRate,
                        deviation=float(delay_days),
                        explanation=(
                            f"Clearing delay is {delay_days} days, which is above the allowed threshold."
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
        """
        Build a standardized anomaly response object.
        """

        transaction = result.transaction

        # Use transactionId if present, otherwise return None
        transaction_id = transaction.get("transactionId")

        # If deviation was not explicitly provided, calculate fee deviation
        if deviation is None and expected_fee is not None and actual_fee is not None:
            deviation = round(actual_fee - expected_fee, 4)

        severity = self._calculate_severity(deviation)

        return TransactionAnomaly(
            transactionId=transaction_id,
            anomalyType=anomaly_type,
            expectedFee=expected_fee,
            actualFee=actual_fee,
            deviation=deviation,
            severity=severity,
            explanation=explanation,
        )

    def _calculate_severity(
        self,
        deviation: float | None,
    ) -> str:
        """
        Convert deviation into severity.

        This is intentionally simple for Phase 1.
        """

        if deviation is None:
            return "MEDIUM"

        if deviation >= 1.0:
            return "HIGH"

        if deviation >= 0.5:
            return "MEDIUM"

        return "LOW"