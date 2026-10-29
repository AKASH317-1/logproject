import re
from datetime import datetime

class LinuxLogParser:
    def __init__(self):
        self.patterns = [
            {
                "event_type": "Failed Login",
                "severity": "HIGH",
                "regex": re.compile(r"Failed password for (?:invalid user )?(\w+) from ([\d.]+)")
            },
            {
                "event_type": "Successful Login",
                "severity": "LOW",
                "regex": re.compile(r"Accepted password for (\w+) from ([\d.]+)")
            },
            {
                "event_type": "Sudo Command",
                "severity": "MEDIUM",
                "regex": re.compile(r"sudo: (\w+).*COMMAND=(.*)")
            },
            {
                "event_type": "User Added",
                "severity": "HIGH",
                "regex": re.compile(r"useradd\[\d+\]: new user: name=(\w+)")
            }
        ]

    def parse_log(self, log_line):
        for pattern in self.patterns:
            match = pattern["regex"].search(log_line)
            if match:
                return self._build_event(pattern, match.groups(), log_line)
        return None

    def _build_event(self, pattern, groups, raw_log):
        event = {
            "timestamp": str(datetime.now()),
            "event_type": pattern["event_type"],
            "severity": pattern["severity"],
            "raw_log": raw_log
        }
        if pattern["event_type"] in ["Failed Login", "Successful Login"]:
            event["username"] = groups[0]
            event["ip"] = groups[1]
        elif pattern["event_type"] == "Sudo Command":
            event["username"] = groups[0]
            event["command"] = groups[1]
        elif pattern["event_type"] == "User Added":
            event["new_user"] = groups[0]
        return event