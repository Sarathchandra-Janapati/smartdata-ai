"""
Run this script once to generate a sample churn dataset for ML training.
Usage: python datasets/generate_sample.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)
N = 2000

tenure = np.random.randint(1, 73, N)
monthly_charges = np.random.uniform(20, 120, N)
total_charges = tenure * monthly_charges + np.random.normal(0, 50, N)
num_products = np.random.randint(1, 6, N)
support_calls = np.random.randint(0, 10, N)
contract_type = np.random.choice(["Month-to-month", "One year", "Two year"], N, p=[0.55, 0.25, 0.20])
internet_service = np.random.choice(["DSL", "Fiber optic", "No"], N, p=[0.40, 0.45, 0.15])
payment_method = np.random.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], N)
gender = np.random.choice(["Male", "Female"], N)
senior_citizen = np.random.choice([0, 1], N, p=[0.84, 0.16])

# Churn probability model
churn_prob = (
    0.3 * (contract_type == "Month-to-month").astype(float) +
    0.2 * (internet_service == "Fiber optic").astype(float) +
    0.1 * (monthly_charges > 80).astype(float) +
    0.15 * (support_calls > 5).astype(float) +
    0.1 * (tenure < 12).astype(float) -
    0.1 * (contract_type == "Two year").astype(float)
)
churn_prob = np.clip(churn_prob, 0.05, 0.95)
churn = (np.random.random(N) < churn_prob).astype(int)

df = pd.DataFrame({
    "customer_id": [f"CUST{str(i).zfill(5)}" for i in range(1, N + 1)],
    "gender": gender,
    "senior_citizen": senior_citizen,
    "tenure": tenure,
    "contract_type": contract_type,
    "internet_service": internet_service,
    "payment_method": payment_method,
    "monthly_charges": monthly_charges.round(2),
    "total_charges": total_charges.round(2),
    "num_products": num_products,
    "support_calls": support_calls,
    "churn": churn,
})

# Introduce 2% missing values for realism
for col in ["monthly_charges", "total_charges", "support_calls"]:
    idx = np.random.choice(N, size=int(N * 0.02), replace=False)
    df.loc[idx, col] = np.nan

output = Path(__file__).parent / "churn_dataset.csv"
df.to_csv(output, index=False)
print(f"Generated {N} records -> {output}")
print(df.head())
print(f"\nChurn rate: {df['churn'].mean()*100:.1f}%")
