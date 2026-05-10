import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

Path("data").mkdir(parents=True, exist_ok=True)

rows = []

conditions = [
    "3DS authentication",
    "clearing time",
    "MCC classification",
]

currencies = ["RON", "EUR"]
countries = ["RO", "DE", "FR", "IT", "ES"]
regions = ["EU", "EEA"]
card_types = ["Credit", "Debit", "Prepaid", "Commercial"]
card_brands = ["VISA", "MASTERCARD"]
mcc_codes = ["5732", "5411", "5812"]
channels = ["eCommerce", "POS", "MOTO"]

fee_rates = [0.0020, 0.0030, 0.0125, 0.0150, 0.0185, 0.0250]

for i in range(500):
    amount = random.randint(20, 5000)
    condition = random.choice(conditions)

    channel = random.choice(channels)
    card_presence = "card_not_present" if channel in ["eCommerce", "MOTO"] else "card_present"

    auth_date = datetime(2026, 5, 1, 10, 0, 0) + timedelta(days=random.randint(0, 20))
    clearing_delay_days = random.choice([0, 1, 2, 3, 4, 5, 7])
    clearing_date = auth_date + timedelta(days=clearing_delay_days)

    fee_rate = random.choice(fee_rates)
    fee_amount = round(amount * fee_rate, 4)

    if condition == "3DS authentication":
        savings = amount * random.uniform(0.004, 0.009)
        suggestion = "ENABLE_3DS"
        success = 1
        three_ds = False
        eci = "07"
    elif condition == "clearing time":
        savings = amount * random.uniform(0.002, 0.005)
        suggestion = "OPTIMIZE_CLEARING"
        success = random.choice([0, 1])
        three_ds = random.choice([True, False])
        eci = "05" if three_ds else "07"
    else:
        savings = amount * random.uniform(0.001, 0.004)
        suggestion = "FIX_MCC"
        success = random.choice([0, 1])
        three_ds = random.choice([True, False])
        eci = "05" if three_ds else "07"

    rows.append({
        # Canonical transaction schema
        "transactionId": f"T-{i + 1}",
        "amount": amount,
        "currency": random.choice(currencies),
        "merchantCountry": random.choice(countries),
        "issuerCountry": random.choice(countries),
        "region": random.choice(regions),
        "cardType": random.choice(card_types),
        "cardBrand": random.choice(card_brands),
        "cardPresence": card_presence,
        "channel": channel,

        # Internal ML feature derived from channel
        "paymentChannel": channel,

        "mcc": random.choice(mcc_codes),
        "threeDS": three_ds,
        "eci": eci,
        "authDate": auth_date.isoformat(),
        "clearingDate": clearing_date.isoformat(),
        "clearingDelayDays": clearing_delay_days,

        # Rule-engine / fee features
        "category": random.choice([
            "Ecom Non-Secure Credit",
            "Ecom Secure Preferred Credit",
            "Standard Credit",
        ]),
        "condition": condition,
        "feeRate": fee_rate,
        "feeAmount": fee_amount,

        # Recommendation ranking features
        "suggestionType": suggestion,
        "expectedImpact": round(savings, 4),
        "difficulty": random.choice(["LOW", "MEDIUM", "HIGH"]),
        "historicalSuccessRate": round(random.uniform(0.3, 0.95), 2),

        # Labels
        "label_actualSavings": round(savings, 4),
        "label_successfulRecommendation": success,
    })

df = pd.DataFrame(rows)
df.to_csv("data/training_data.csv", index=False)

print("Generated data/training_data.csv")
print(df.head())
print("Max feeRate:", df["feeRate"].max())