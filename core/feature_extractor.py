def extract_features(log_str: str, event_type: str = "") -> list:
    """
    Extracts 3 binary features from log string and event type.
    Returns [failed_login, malware, download]
    """
    features = {
        "failed_login": 0,
        "malware": 0,
        "download": 0
    }

    # 1. Check event_type first (most reliable for Windows)
    if event_type:
        et_lower = event_type.lower()
        if "failed" in et_lower or "fail" in et_lower:
            features["failed_login"] = 1

    # 2. If not set, search raw log string
    if features["failed_login"] == 0:
        log_lower = log_str.lower()
        if "failed" in log_lower or "fail" in log_lower:
            features["failed_login"] = 1
        if "malware" in log_lower:
            features["malware"] = 1
        if "download" in log_lower:
            features["download"] = 1

    return list(features.values())