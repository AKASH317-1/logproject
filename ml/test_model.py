import joblib

# Load trained model
model = joblib.load("models/anomaly_model.pkl")

# Test samples
samples = [
    [0,0,0],
    [1,0,0],
    [0,1,0],
    [1,1,1]
]

for sample in samples:
    result = model.predict([sample])[0]

    if result == -1:
        print(f"🚨 Suspicious Activity: {sample}")
    else:
        print(f"✅ Normal Activity: {sample}")