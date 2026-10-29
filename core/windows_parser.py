WINDOWS_EVENTS = {
    4624: "Successful Login",
    4625: "Failed Login",
    4688: "Process Created",
    1102: "Logs Cleared",
    4720: "User Created"
}

def parse_windows_log(log_dict):
    event_id = log_dict.get("event_id")
    return {
        "event_type": WINDOWS_EVENTS.get(event_id, "Unknown"),
        "raw_log": log_dict.get("raw", ""),
        "timestamp": log_dict.get("time"),
        "source": log_dict.get("source")
    }