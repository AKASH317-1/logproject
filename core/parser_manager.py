from .linux_parser import LinuxLogParser
from .windows_parser import parse_windows_log
from .firewall_parser import parse_firewall_log

class ParserManager:
    def __init__(self):
        self.linux_parser = LinuxLogParser()

    def parse(self, source, log):
        if source == "linux":
            return self.linux_parser.parse_log(log)
        elif source == "windows":
            return parse_windows_log(log)
        elif source == "firewall":
            return parse_firewall_log(log)
        return None