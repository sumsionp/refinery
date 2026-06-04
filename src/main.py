import argparse
import sys
import os
import curses
from src.db import init_db
from src.archive_utils import process_new_archive
from src.case_manager import set_active_cases, cleanup_expired_data, get_case_status
from src.tui import ManualGateTUI
from src.scrubber import Scrubber

def main():
    parser = argparse.ArgumentParser(description="Refinery: Support Case Intelligence Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Gather command
    gather_parser = subparsers.add_parser("gather", help="Import a raw support archive")
    gather_parser.add_argument("case_id", help="The Case ID to associate with the archive")
    gather_parser.add_argument("archive", help="Path to the .tar.gz, .zip, etc. archive")

    # Review command
    review_parser = subparsers.add_parser("review", help="Review and scrub a file in a case")
    review_parser.add_argument("case_id", help="The Case ID")
    review_parser.add_argument("file_path", help="Path to the file within data/raw/case_id/")

    # Cases command
    cases_parser = subparsers.add_parser("cases", help="Manage active cases and cleanup")
    cases_parser.add_argument("--active", nargs="*", help="List of active case IDs")
    cases_parser.add_argument("--cleanup", action="store_true", help="Run cleanup for expired cases")
    cases_parser.add_argument("--immediate", action="store_true", help="Cleanup pending deletions immediately")
    cases_parser.add_argument("--status", action="store_true", help="Show status of all cases")

    args = parser.parse_args()

    if args.command == "gather":
        init_db()
        process_new_archive(args.case_id, args.archive)

    elif args.command == "review":
        init_db()
        # If file_path is relative to the case dir, prepend it
        full_path = args.file_path
        if not os.path.exists(full_path):
            full_path = os.path.join("data", "raw", args.case_id, args.file_path)

        if os.path.exists(full_path):
            tui = ManualGateTUI(args.case_id, full_path)
            curses.wrapper(tui.run)
        else:
            print(f"Error: File {full_path} not found.")

    elif args.command == "cases":
        init_db()
        if args.active is not None:
            set_active_cases(args.active)
            print(f"Updated active cases: {args.active}")

        if args.cleanup:
            cleanup_expired_data(immediate=args.immediate)

        if args.status:
            print(f"{'Case ID':<15} | {'Status':<15} | {'Deletion Date'}")
            print("-" * 50)
            for row in get_case_status():
                print(f"{row['case_id']:<15} | {row['status']:<15} | {row['deletion_date']}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
