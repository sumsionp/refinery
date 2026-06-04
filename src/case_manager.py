import os
import shutil
from datetime import datetime, timedelta
from src.db import get_db_connection

def set_active_cases(active_case_ids):
    """
    Sets the list of active cases. Any case NOT in this list that was
    previously active will be marked for deletion in 30 days.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Ensure all active cases are in the database and active
    for case_id in active_case_ids:
        cursor.execute("""
            INSERT INTO cases (case_id, status, deletion_date)
            VALUES (?, 'active', NULL)
            ON CONFLICT(case_id) DO UPDATE SET status='active', deletion_date=NULL
        """, (case_id,))

    # 2. Mark cases not in the list for deletion
    placeholders = ','.join(['?'] * len(active_case_ids))
    deletion_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

    if active_case_ids:
        cursor.execute(f"""
            UPDATE cases SET status='pending_deletion', deletion_date=?
            WHERE case_id NOT IN ({placeholders}) AND status='active'
        """, [deletion_date] + active_case_ids)
    else:
        cursor.execute("UPDATE cases SET status='pending_deletion', deletion_date=? WHERE status='active'", (deletion_date,))

    conn.commit()
    conn.close()

def cleanup_expired_data(immediate=False):
    """
    Deletes raw data for cases that have passed their deletion date.
    If immediate=True, deletes all cases marked as 'pending_deletion'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if immediate:
        cursor.execute("SELECT case_id FROM cases WHERE status='pending_deletion'")
    else:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("SELECT case_id FROM cases WHERE status='pending_deletion' AND deletion_date <= ?", (now,))

    expired_cases = [row['case_id'] for row in cursor.fetchall()]

    for case_id in expired_cases:
        raw_dir = os.path.join("data", "raw", case_id)
        if os.path.exists(raw_dir):
            print(f"Cleaning up raw data for case {case_id}...")
            shutil.rmtree(raw_dir)

        cursor.execute("UPDATE cases SET status='deleted' WHERE case_id=?", (case_id,))

    conn.commit()
    conn.close()

def get_case_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT case_id, status, deletion_date FROM cases")
    rows = cursor.fetchall()
    conn.close()
    return rows
