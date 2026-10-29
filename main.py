import threading
import sys
import os
from queue import Queue

# Add project directories to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.parser_manager import ParserManager
from core.filters import LogFilter
from core.normalize import LogNormalizer
from core.feature_extractor import extract_features
import joblib

# Import collector functions
from collectors.linux_collector import start_linux
from collectors.windows_collector import start_windows
from collectors.server_collector import start_server

# Load ML model
model_path = os.path.join("ml", "models", "anomaly_model.pkl")
if not os.path.exists(model_path):
    print(f"❌ Model not found at {model_path}. Please run ml/train_model.py first.")
    sys.exit(1)
model = joblib.load(model_path)

# Shared queue
log_queue = Queue()

def process_logs():
    """Main processing loop: parse → filter → normalize → feature extract → predict → alert"""
    parser_mgr = ParserManager()
    log_filter = LogFilter()
    normalizer = LogNormalizer()

    while True:
        source, raw_log = log_queue.get()
        # 1. Parse
        parsed = parser_mgr.parse(source, raw_log)
        if not parsed:
            continue
        # 2. Filter (whitelist/blacklist)
        filtered = log_filter.filter_event(parsed)
        if not filtered:
            continue
        # 3. Normalize to standard schema
        normalized = normalizer.normalize(filtered)
        # 4. Extract features (use raw_log string)
        log_str = normalized.get("raw_log", "")
        if isinstance(log_str, dict):
            log_str = str(log_str)
        features = extract_features(log_str)
        # 5. Predict
        pred = model.predict([features])[0]
        # 6. Alert or log
        if pred == -1:
            print(f"🚨 ALERT [{source}]: {normalized.get('event_type', 'Unknown')} | {log_str[:200]}")
        else:
            print(f"✅ NORMAL [{source}]: {normalized.get('event_type', 'Unknown')}")

def main():
    # Start collector threads
    threads = [
        threading.Thread(target=start_linux, args=(log_queue,), daemon=True),
        threading.Thread(target=start_windows, args=(log_queue,), daemon=True),
        threading.Thread(target=start_server, args=(log_queue,), daemon=True),
        threading.Thread(target=process_logs, daemon=True)
    ]
    for t in threads:
        t.start()

    print("🚀 Real‑time AI Log Analyzer Running. Press Ctrl+C to stop.\n")
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()