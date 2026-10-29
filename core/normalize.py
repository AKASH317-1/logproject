from copy import deepcopy
from .schema import STANDARD_SCHEMA

class LogNormalizer:
    def normalize(self, parsed_log):
        normalized = deepcopy(STANDARD_SCHEMA)
        for key in normalized.keys():
            if key in parsed_log:
                normalized[key] = parsed_log[key]
        return normalized