import joblib
import os
from sklearn.ensemble import IsolationForest

os.makedirs("models", exist_ok=True)

# Normal: 1000 rows of [0,0,0]
normal = [[0,0,0] for _ in range(1000)]

# Anomalies: all combinations where failed_login = 1 (strong signal)
anomaly = [[1,0,0], [1,1,0], [1,0,1], [1,1,1]] * 20   # 80 strong anomalies

X_train = normal + anomaly
# Lower contamination to make model more sensitive to anomalies
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_train)

joblib.dump(model, "models/anomaly_model.pkl")
print("✅ Model retrained with strong failed_login anomalies and lower contamination (0.1)")