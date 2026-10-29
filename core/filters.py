from .whitelist import WHITELISTED_IPS, WHITELISTED_USERS
from .blacklist import BLACKLISTED_IPS, BLACKLISTED_COMMANDS

class LogFilter:
    def filter_event(self, event):
        if not event:
            return None

        ip = event.get("ip")
        username = event.get("username")
        command = event.get("command", "")

        # Whitelist
        if ip in WHITELISTED_IPS:
            return None
        if username in WHITELISTED_USERS:
            return None

        # Blacklist
        if ip in BLACKLISTED_IPS:
            event["blacklisted_ip"] = True
            event["severity"] = "CRITICAL"

        for bad_cmd in BLACKLISTED_COMMANDS:
            if bad_cmd.lower() in command.lower():
                event["dangerous_command"] = True
                event["severity"] = "CRITICAL"

        return event