import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

import joblib

# =====================================
# LOAD DATASET
# =====================================

df = pd.read_csv(
    "backend/ml/orders_training.csv"
)

# =====================================
# ENCODE STATUS
# =====================================

status_encoder = LabelEncoder()

df["status"] = status_encoder.fit_transform(
    df["status"]
)

# =====================================
# ENCODE TARGET COLUMN
# =====================================

risk_encoder = LabelEncoder()

df["delay_risk"] = risk_encoder.fit_transform(
    df["delay_risk"]
)

# =====================================
# FEATURES & TARGET
# =====================================

X = df[
    [
        "inventory_available",
        "status",
        "sla_days"
    ]
]

y = df["delay_risk"]

# =====================================
# TRAIN MODEL
# =====================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# =====================================
# SAVE MODEL
# =====================================

joblib.dump(
    model,
    "backend/ml/model.pkl"
)

joblib.dump(
    status_encoder,
    "backend/ml/status_encoder.pkl"
)

joblib.dump(
    risk_encoder,
    "backend/ml/risk_encoder.pkl"
)

print("Model Trained Successfully")