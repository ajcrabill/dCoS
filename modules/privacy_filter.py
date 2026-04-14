"""Privacy Filtering: Strip sensitive data before storage.

Removes API keys, credentials, passwords, and other sensitive data from
observations before storing them in the database.
"""

import re
from typing import Dict, Any, List


class PrivacyFilter:
    """Strips sensitive data from observations."""

    PATTERNS = {
        "api_key": [
            r"sk-[a-zA-Z0-9]{20,}",
            r"['\\\"]?api[_-]?key['\\\"]?\\s*[=::]\\s*['\\\"][^'\\\"]+['\\\"]",
        ],
        "password": [
            r"['\\\"]?password['\\\"]?\\s*[=::]\\s*['\\\"][^'\\\"]+['\\\"]",
            r"password\\s*[=::]\\s*\\S+",
        ],
        "token": [
            r"['\\\"]?token['\\\"]?\\s*[=::]\\s*['\\\"][^'\\\"]+['\\\"]",
            r"token\\s*[=::]\\s*\\S+",
        ],
        "secret": [
            r"['\\\"]?secret['\\\"]?\\s*[=::]\\s*['\\\"][^'\\\"]+['\\\"]",
            r"secret\\s*[=::]\\s*\\S+",
        ],
        "credentials": [
            r\"['\\\"]?credentials['\\\"]?\\s*[=::]\\s*\\{[^}]+\\}\",\n        ],\n        \"email\": [\n            r\"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\",\n        ],\n        \"phone\": [\n            r\"\\\\+?1?\\\\s?\\\\(?[0-9]{3}\\\\)?[\\\\s.-]?[0-9]{3}[\\\\s.-]?[0-9]{4}\",\n        ],\n        \"ssn\": [\n            r\"\\\\d{3}-\\\\d{2}-\\\\d{4}\",  # XXX-XX-XXXX\n        ],\n    }\n\n    def __init__(self, redaction_level: str = \"medium\"):\n        \"\"\"Initialize privacy filter.\n\n        Args:\n            redaction_level: \"strict\" (redact all), \"medium\" (default), \"light\"\n        \"\"\"\n        self.redaction_level = redaction_level\n\n    def filter_text(self, text: str) -> str:\n        \"\"\"Filter sensitive data from text.\n\n        Args:\n            text: Input text\n\n        Returns:\n            Text with sensitive data redacted\n        \"\"\"\n        if not isinstance(text, str):\n            return text\n\n        for category, patterns in self.PATTERNS.items():\n            # Always redact critical categories\n            if self.redaction_level == \"strict\" or category in [\"api_key\", \"password\", \"token\", \"secret\"]:\n                for pattern in patterns:\n                    text = re.sub(pattern, f\"[REDACTED_{category.upper()}]\", text, flags=re.IGNORECASE)\n\n        return text\n\n    def filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Filter sensitive data from dictionary.\n\n        Args:\n            data: Input dictionary\n\n        Returns:\n            Dictionary with sensitive values redacted\n        \"\"\"\n        filtered = {}\n        for key, value in data.items():\n            if isinstance(value, str):\n                filtered[key] = self.filter_text(value)\n            elif isinstance(value, dict):\n                filtered[key] = self.filter_dict(value)\n            elif isinstance(value, list):\n                filtered[key] = [self.filter_text(v) if isinstance(v, str) else v for v in value]\n            else:\n                filtered[key] = value\n        return filtered\n\n    def filter_observations(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:\n        \"\"\"Filter a list of observations.\n\n        Args:\n            observations: List of observation dictionaries\n\n        Returns:\n            List with sensitive data redacted\n        \"\"\"\n        return [self.filter_dict(obs) for obs in observations]\n"}}]
