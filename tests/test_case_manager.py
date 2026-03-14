import unittest
import os
import shutil
from datetime import datetime, timedelta
from src.db import init_db, get_db_connection
from src.case_manager import set_active_cases, cleanup_expired_data, get_case_status

class TestCaseManager(unittest.TestCase):
    def setUp(self):
        init_db()
        self.raw_base = "data/raw"
        os.makedirs(self.raw_base, exist_ok=True)

    def test_active_case_management(self):
        # 1. Create a case and its raw data
        case_id = "CASE-1"
        os.makedirs(os.path.join(self.raw_base, case_id), exist_ok=True)

        # 2. Set it as active
        set_active_cases([case_id])
        status = get_case_status()
        self.assertEqual(status[0]['status'], 'active')

        # 3. Set a different list as active (marking CASE-1 for deletion)
        set_active_cases(["CASE-2"])
        status = {row['case_id']: row['status'] for row in get_case_status()}
        self.assertEqual(status[case_id], 'pending_deletion')

        # 4. Cleanup immediately
        cleanup_expired_data(immediate=True)
        self.assertFalse(os.path.exists(os.path.join(self.raw_base, case_id)))

        status = {row['case_id']: row['status'] for row in get_case_status()}
        self.assertEqual(status[case_id], 'deleted')

if __name__ == '__main__':
    unittest.main()
