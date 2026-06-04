import re
import hashlib
import uuid
from src.db import get_db_connection

class Scrubber:
    def __init__(self, salt=None):
        self.salt = salt or self._get_or_create_salt()
        self.pii_patterns = {
            'ipv4': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'ipv6': r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))',
            'mac': r'\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'fqdn': r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        }

    def _get_or_create_salt(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'salt'")
        row = cursor.fetchone()
        if row:
            salt = row['value']
        else:
            salt = uuid.uuid4().hex
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('salt', salt))
            conn.commit()
        conn.close()
        return salt

    def _hash_value(self, value, label):
        hash_obj = hashlib.sha256((value + self.salt).encode())
        # Return a shortened hash with a label for readability
        return f"[{label}:{hash_obj.hexdigest()[:8]}]"

    def scrub(self, text, proprietary_terms=None):
        scrubbed_text = text

        # 1. Scrub common PII using regex
        for label, pattern in self.pii_patterns.items():
            matches = set(re.findall(pattern, scrubbed_text))
            for match in matches:
                # We want to avoid double-scrubbing or scrubbing parts of already scrubbed content
                # A simple replacement for now, though it has limitations
                scrubbed_text = scrubbed_text.replace(match, self._hash_value(match, label.upper()))

        # 2. Scrub proprietary terms
        if proprietary_terms:
            for term in proprietary_terms:
                if term:
                    # Case-insensitive replacement for proprietary terms
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    scrubbed_text = pattern.sub(f"[PROPRIETARY:{hashlib.sha256((term.lower() + self.salt).encode()).hexdigest()[:8]}]", scrubbed_text)

        return scrubbed_text

if __name__ == "__main__":
    scrubber = Scrubber()
    sample = "Connect to 192.168.1.1 or mail admin@company.com on server1.internal.company.com"
    print(f"Original: {sample}")
    print(f"Scrubbed: {scrubber.scrub(sample)}")
