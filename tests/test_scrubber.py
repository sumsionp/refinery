import unittest
from src.scrubber import Scrubber
from src.db import init_db
import os

class TestScrubber(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.scrubber = Scrubber(salt="test_salt")

    def test_ipv4_scrubbing(self):
        text = "My IP is 192.168.1.50."
        scrubbed = self.scrubber.scrub(text)
        self.assertNotIn("192.168.1.50", scrubbed)
        self.assertIn("[IPV4:", scrubbed)

    def test_email_scrubbing(self):
        text = "Contact us at support@example.com"
        scrubbed = self.scrubber.scrub(text)
        self.assertNotIn("support@example.com", scrubbed)
        self.assertIn("[EMAIL:", scrubbed)

    def test_fqdn_scrubbing(self):
        text = "Check the logs on app-server-01.internal.network.local"
        scrubbed = self.scrubber.scrub(text)
        self.assertNotIn("app-server-01.internal.network.local", scrubbed)
        self.assertIn("[FQDN:", scrubbed)

    def test_consistency(self):
        text1 = "10.0.0.1"
        text2 = "10.0.0.1"
        self.assertEqual(self.scrubber.scrub(text1), self.scrubber.scrub(text2))

    def test_proprietary_terms(self):
        text = "The Project Phoenix is top secret."
        terms = ["Project Phoenix"]
        scrubbed = self.scrubber.scrub(text, terms)
        self.assertNotIn("Project Phoenix", scrubbed)
        self.assertIn("[PROPRIETARY:", scrubbed)

if __name__ == '__main__':
    unittest.main()
