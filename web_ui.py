from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import sys
import os
from queue import Queue

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing modules
from collectors.linux_collector import start_linux
from collectors.windows_collector import start_windows
from collectors.server_collector import start_server
from core.parser_manager import ParserManager
from core.filters import LogFilter
from core.normalize import LogNormalizer
from core.feature_extractor import extract_features
import joblib

# Shared queue for raw logs (same as in main.py)
log_queue = Queue()
alert_queue = Queue()

# Load ML model
model = joblib.load("ml/models/anomaly_model.pkl")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for last 100 logs and 50 alerts
log_history = []
alert_history = []

def process_logs():
    """Same logic as in main.py – parses, filters, predicts, and pushes alerts."""
    parser_mgr = ParserManager()
    log_filter = LogFilter()
    normalizer = LogNormalizer()

    while True:
        source, raw_log = log_queue.get()
        parsed = parser_mgr.parse(source, raw_log)
        if not parsed:
            continue
        filtered = log_filter.filter_event(parsed)
        if not filtered:
            continue
        normalized = normalizer.normalize(filtered)

        log_str = normalized.get("raw_log", "")
        if isinstance(log_str, dict):
            log_str = str(log_str)
        event_type = normalized.get("event_type", "")
        features = extract_features(log_str, event_type)

        pred = model.predict([features])[0]

        if pred == -1:
            msg = f"[{source}] {event_type} | {log_str[:200]}"
            alert_queue.put({"timestamp": time.strftime("%H:%M:%S"), "message": msg})

def background_processor():
    """Reads raw logs from queue and sends to WebSocket."""
    while True:
        source, raw = log_queue.get()
        entry = {
            "source": source,
            "raw": str(raw)[:200],
            "timestamp": time.strftime("%H:%M:%S")
        }
        log_history.append(entry)
        if len(log_history) > 100:
            log_history.pop(0)
        socketio.emit('new_log', entry)

def alert_broadcaster():
    """Reads alerts from queue and sends to WebSocket."""
    while True:
        alert = alert_queue.get()
        alert_history.append(alert)
        if len(alert_history) > 50:
            alert_history.pop(0)
        socketio.emit('new_alert', alert)

@app.route('/')
def index():
    return render_template('index.html', logs=log_history, alerts=alert_history)

@socketio.on('connect')
def handle_connect():
    emit('init', {'logs': log_history, 'alerts': alert_history})

def start_background_threads():
    """Start all collector threads, processing thread, and UI broadcasters."""
    # Collectors
    threads = [
        threading.Thread(target=start_linux, args=(log_queue,), daemon=True),
        threading.Thread(target=start_windows, args=(log_queue,), daemon=True),
        threading.Thread(target=start_server, args=(log_queue,), daemon=True),
        # Processing and broadcasting
        threading.Thread(target=process_logs, daemon=True),
        threading.Thread(target=background_processor, daemon=True),
        threading.Thread(target=alert_broadcaster, daemon=True)
    ]
    for t in threads:
        t.start()

if __name__ == '__main__':
    start_background_threads()
    print("🌐 Web UI starting at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)