import os
import tarfile
import zipfile
import shutil
import lzma
import subprocess

def unpack_archive(archive_path, extract_to):
    """
    Unpacks various archive types into the specified directory.
    Supported: .tar.gz, .tgz, .tar.xz, .xz, .zip, .7z
    """
    os.makedirs(extract_to, exist_ok=True)

    if archive_path.endswith(('.tar.gz', '.tgz')):
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(path=extract_to)
        return True
    elif archive_path.endswith(('.tar.xz', '.xz')):
        try:
            with tarfile.open(archive_path, 'r:xz') as tar:
                tar.extractall(path=extract_to)
        except tarfile.ReadError:
            # If it's just a raw xz file (not a tar), we handle it differently
            # For simplicity in this tool, we'll assume it's usually a tar.xz if it's a supportconfig
            # but let's add a basic check
            return False
        return True
    elif archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    elif archive_path.endswith('.7z'):
        # 7zip usually requires the '7z' command line tool
        try:
            subprocess.run(['7z', 'x', archive_path, f'-o{extract_to}', '-y'], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: '7z' command not found. Please install p7zip.")
            return False

    return False

def get_case_raw_dir(case_id):
    return os.path.join("data", "raw", case_id)

def process_new_archive(case_id, archive_path):
    extract_to = get_case_raw_dir(case_id)
    if unpack_archive(archive_path, extract_to):
        print(f"Successfully unpacked {archive_path} to {extract_to}")

        # Register in database
        from src.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Register/Update Case
        cursor.execute("""
            INSERT INTO cases (case_id, status) VALUES (?, 'active')
            ON CONFLICT(case_id) DO UPDATE SET status='active', deletion_date=NULL
        """, (case_id,))

        # 2. Register Files
        for root, _, files in os.walk(extract_to):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, extract_to)
                cursor.execute("""
                    INSERT INTO files (case_id, file_path, file_type)
                    VALUES (?, ?, ?)
                """, (case_id, rel_path, os.path.splitext(file)[1]))

        conn.commit()
        conn.close()
        return extract_to
    else:
        print(f"Failed to unpack {archive_path}")
        return None
