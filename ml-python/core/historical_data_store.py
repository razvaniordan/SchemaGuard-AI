from typing import Dict, List, Optional
import pandas as pd

from models.analysis_models import HistoricalMLRecord, HistoricalDataStoreResult


class HistoricalDataStore:
    def __init__(self, duplicate_strategy: str = "update") -> None:
        self.records: Dict[str, HistoricalMLRecord] = {}
        self.duplicate_strategy = duplicate_strategy

    def store(
        self,
        record: HistoricalMLRecord,
    ) -> HistoricalDataStoreResult:
        warnings = []

        if not record.transactionId:
            return HistoricalDataStoreResult(
                stored=False,
                transactionId=None,
                warnings=["Missing transactionId. Record skipped."],
            )

        if not record.features:
            return HistoricalDataStoreResult(
                stored=False,
                transactionId=record.transactionId,
                warnings=["Missing features. Record skipped."],
            )

        if record.labels is None:
            warnings.append("Missing labels. Stored as unlabeled record.")

        if record.transactionId in self.records:
            if self.duplicate_strategy == "skip":
                return HistoricalDataStoreResult(
                    stored=False,
                    transactionId=record.transactionId,
                    warnings=["Duplicate transactionId. Record skipped."],
                )

            warnings.append("Duplicate transactionId. Existing record updated.")

        self.records[record.transactionId] = record

        return HistoricalDataStoreResult(
            stored=True,
            transactionId=record.transactionId,
            warnings=warnings,
        )

    def get_all(self) -> List[HistoricalMLRecord]:
        return list(self.records.values())

    def to_dataframe(self) -> pd.DataFrame:
        rows = []

        for record in self.records.values():
            row = {
                "transactionId": record.transactionId,
                "timestamp": record.timestamp,
                "modelVersion": record.modelVersion,
                "algorithmUsed": record.algorithmUsed,
            }

            row.update(record.features)

            if record.labels:
                for key, value in record.labels.items():
                    row[f"label_{key}"] = value

            rows.append(row)

        return pd.DataFrame(rows)