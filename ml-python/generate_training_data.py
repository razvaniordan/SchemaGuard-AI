import random
import pandas as pd

random.seed(42)

rows = []

conditions = [
    "3DS authentication",
    "clearing time",
    "MCC classification",
]

for i in range(500):
    amount = random.randint(20, 5000)
    condition = random.choice(conditions)

    if condition == "3DS authentication":
        savings = amount * random.uniform(0.004, 0.009)
        suggestion = "ENABLE_3DS"
        success = 1
    elif condition == "clearing time":
        savings = amount * random.uniform(0.002, 0.005)
        suggestion = "OPTIMIZE_CLEARING"
        success = random.choice([0, 1])
    else:
        savings = amount * random.uniform(0.001, 0.004)
        suggestion = "FIX_MCC"
        success = random.choice([0, 1])

    rows.append({
        "amount": amount,
        "feeRate": random.choice([1.25, 1.55, 1.85]),
        "feeAmount": round(amount * 0.0185, 2),
        "clearingDelayDays": random.choice([1, 2, 3, 4, 5]),
        "category": random.choice([
            "Ecom Non-Secure Credit",
            "Ecom Secure Preferred Credit",
            "Standard Credit",
        ]),
        "condition": condition,
        "paymentChannel": "eCommerce",
        "threeDS": condition != "3DS authentication",
        "mcc": random.choice(["5732", "5411", "5812"]),
        "label_actualSavings": round(savings, 2),

        "suggestionType": suggestion,
        "expectedImpact": round(savings, 2),
        "difficulty": random.choice(["LOW", "MEDIUM", "HIGH"]),
        "historicalSuccessRate": round(random.uniform(0.3, 0.95), 2),
        "label_successfulRecommendation": success,
    })

df = pd.DataFrame(rows)
df.to_csv("data/training_data.csv", index=False)

print("Generated data/training_data.csv")
print(df.head())