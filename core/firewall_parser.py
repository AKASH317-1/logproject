import re

FIREWALL_REGEX = re.compile(
    r"(DROP|ALLOW)\s+(\w+)\s+([\d.]+)\s+->\s+([\d.]+)\s+PORT\s+(\d+)"
)

def parse_firewall_log(log_str):
    match = FIREWALL_REGEX.search(log_str)
    if not match:
        return None
    return {
        "action": match.group(1),
        "protocol": match.group(2),
        "src_ip": match.group(3),
        "dst_ip": match.group(4),
        "port": int(match.group(5)),
        "raw_log": log_str,
        "event_type": "Firewall Rule"
    }