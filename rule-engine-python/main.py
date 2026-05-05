"""FastAPI skeleton for the SchemeGuard rule engine service.

Story 2.2.2: rule-engine-python structure + FastAPI skeleton.

This service exposes the initial REST contract for transaction classification.
The actual ClassificationEngine implementation will be added in later subtasks.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
    CardType,
    Channel,
    ClassificationRequest,
    ClassificationResponse,
    EU_PHASE_1_CATEGORY_DEFINITIONS,
    Region,
)

APP_NAME = "SchemeGuard Rule Engine"
APP_VERSION = "0.1.0"
PHASE = "EU Phase 1"


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Python rule engine service for transaction classification, "
        "interchange category selection, and future scheme compliance checks."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:4200",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Simple healthcheck endpoint for local dev, CI, and Java integration."""

    return {
        "status": "UP",
        "service": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/metadata", tags=["system"])
def metadata() -> dict[str, object]:
    """Return service metadata and supported classification dimensions."""

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "phase": PHASE,
        "supportedPriorities": {
            "min": 1,
            "max": 14,
        },
        "supportedChannels": [
            Channel.POS.value,
            Channel.ECOMMERCE.value,
            Channel.MOTO.value,
        ],
        "supportedCardTypes": [
            CardType.CREDIT.value,
            CardType.DEBIT.value,
            CardType.COMMERCIAL.value,
            CardType.PREPAID.value,
        ],
        "supportedRegions": [
            Region.EU.value,
            Region.CROSS_BORDER.value,
        ],
    }


@app.get("/categories", tags=["classification"])
def categories() -> list[dict[str, object]]:
    """Return the configured EU Phase 1 classification categories.

    This is useful for UI debugging and Java backend integration checks.
    """

    return [
        category.model_dump(by_alias=True, mode="json")
        for category in EU_PHASE_1_CATEGORY_DEFINITIONS
    ]


@app.post(
    "/classify-transaction",
    response_model=ClassificationResponse,
    tags=["classification"],
)
def classify_transaction(request: ClassificationRequest) -> ClassificationResponse:
    """Validate the request contract for future classification.

    The ClassificationEngine is intentionally not implemented in Story 2.2.2.
    It will be added in the following subtasks.
    """

    raise HTTPException(
        status_code=501,
        detail=(
            "ClassificationEngine is not implemented yet. "
            "Story 2.2.3+ will add priority-based rule evaluation."
        ),
    )