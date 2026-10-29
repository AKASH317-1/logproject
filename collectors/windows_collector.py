import win32evtlog
import time
from queue import Queue

def start_windows(log_queue: Queue):
    hand = win32evtlog.OpenEventLog('localhost', 'Security')
    # Keep a set of already processed event IDs (record number + time) to avoid duplicates
    processed = set()
    
    print("[+] Windows EventLog monitoring started (incremental, no seek errors).")

    while True:
        try:
            # Read the last 100 events (enough to catch new ones)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events = win32evtlog.ReadEventLog(hand, flags, 100)
            if events:
                # Events come in reverse chronological order (newest first)
                for event in events:
                    # Create a unique ID: record number + time generated
                    event_id = f"{event.RecordNumber}_{event.TimeGenerated}"
                    if event_id not in processed:
                        processed.add(event_id)
                        log_data = {
                            "event_id": event.EventID & 0xFFFF,
                            "source": event.SourceName,
                            "time": str(event.TimeGenerated),
                            "raw": str(event.StringInserts) if hasattr(event, 'StringInserts') else "",
                            "record_number": event.RecordNumber
                        }
                        log_queue.put(("windows", log_data))
                # Keep only last 5000 IDs to avoid memory bloat
                if len(processed) > 5000:
                    # Remove oldest 2500 (simple way: convert to list, slice, back to set)
                    processed = set(list(processed)[-2500:])
            time.sleep(1)
        except Exception as e:
            print(f"[!] Windows collector error: {e}")
            time.sleep(1)