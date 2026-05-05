from __future__ import annotations
"""3DS / ECI authentication evaluation logic.

Story 2.2.6: 3DS / ECI evaluation logic.

For EU Phase 1:
- ECI 05 and 06 are considered secure.
- Other present ECI values are considered non-secure.
- If ECI is missing, the threeDS boolean is used as fallback.
"""



import logging
from dataclasses import dataclass

from models import AuthStatus, TransactionInput

logger = logging.getLogger(__name__)


SECURE_ECI_VALUES = {"05", "06"}


@dataclass(frozen=True)
class AuthenticationEvaluation:
    """Derived authentication status for a transaction."""

    status: AuthStatus
    source: str
    reason_code: str | None = None
    message: str | None = None


class AuthenticationEvaluator:
    """Evaluate 3DS / ECI status for interchange classification."""

    def evaluate(self, transaction: TransactionInput) -> AuthenticationEvaluation:
        """Derive authentication status from ECI and threeDS flag.

        ECI takes precedence over the boolean threeDS flag.
        """

        if transaction.eci in SECURE_ECI_VALUES:
            return AuthenticationEvaluation(
                status=AuthStatus.SECURE,
                source="eci",
                reason_code="SECURE_ECI",
                message=f"ECI {transaction.eci} is secure.",
            )

        if transaction.eci is not None:
            if transaction.three_ds is True:
                logger.info(
                    "ECI indicates non-secure although threeDS=true for transaction_id=%s eci=%s",
                    transaction.transaction_id,
                    transaction.eci,
                )

            return AuthenticationEvaluation(
                status=AuthStatus.NON_SECURE,
                source="eci",
                reason_code="NON_SECURE_ECI",
                message=f"ECI {transaction.eci} is not secure.",
            )

        if transaction.three_ds is True:
            return AuthenticationEvaluation(
                status=AuthStatus.SECURE,
                source="threeDS",
                reason_code="SECURE_THREEDS_FLAG",
                message="threeDS flag indicates secure authentication.",
            )

        if transaction.three_ds is False:
            return AuthenticationEvaluation(
                status=AuthStatus.NON_SECURE,
                source="threeDS",
                reason_code="NON_SECURE_THREEDS_FLAG",
                message="threeDS flag indicates non-secure authentication.",
            )

        logger.info(
            "Missing 3DS and ECI authentication data for transaction_id=%s",
            transaction.transaction_id,
        )

        return AuthenticationEvaluation(
            status=AuthStatus.UNKNOWN,
            source="missing",
            reason_code="MISSING_AUTH_STATUS",
            message="Both ECI and threeDS are missing.",
        )