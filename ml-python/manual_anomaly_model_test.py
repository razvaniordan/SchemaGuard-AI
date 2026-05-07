from core.ml_anomaly_detection_model import MLAnomalyDetectionModel


model = MLAnomalyDetectionModel()
model.load("models/artifacts/anomaly-model-v1.joblib")

transactions = [
    {
        "transactionId": "normal-1",
        "amount": 120,
        "feeRate": 1.25,
        "feeAmount": 1.5,
        "clearingDelayDays": 1,
        "category": "Ecom Secure Preferred Credit",
        "paymentChannel": "eCommerce",
        "threeDS": True,
        "mcc": "5732",
    },
    {
        "transactionId": "anomaly-1",
        "amount": 9999,
        "feeRate": 4.99,
        "feeAmount": 499.0,
        "clearingDelayDays": 9,
        "category": "Ecom Secure Preferred Credit",
        "paymentChannel": "eCommerce",
        "threeDS": False,
        "mcc": "9999",
    },
]

results = model.detect_batch(transactions)

print("Detected anomalies:")
for result in results:
    print(result.model_dump())