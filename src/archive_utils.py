import os
import tarfile
import zipfile
import shutil
import lzma
import subprocess

def unpack_archive(archive_path, extract_to):
    """
    Unpacks various archive types into the specified directory.
    Supported: .tar.gz, .tgz, .tar.xz, .xz, .txz, .zip, .7z
    """
    os.makedirs(extract_to, exist_ok=True)

    try:
        if archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(path=extract_to)
            return True
        elif archive_path.endswith(('.tar.xz', '.xz', '.txz')):
            try:
                with tarfile.open(archive_path, 'r:xz') as tar:
                    tar.extractall(path=extract_to)
                return True
            except (tarfile.ReadError, lzma.LZMAError):
                # If it's just a raw xz file (not a tar), decompress it
                if archive_path.endswith('.txz'):
                    out_filename = os.path.basename(archive_path)[:-4]
                else:
                    out_filename = os.path.basename(archive_path)[:-3]

                out_path = os.path.join(extract_to, out_filename)
                with lzma.open(archive_path, 'rb') as f_in:
                    with open(out_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # If the resulting file is a tarball, extract it too
                if tarfile.is_tarfile(out_path):
                    with tarfile.open(out_path, 'r') as tar:
                        tar.extractall(path=extract_to)
                    os.remove(out_path)
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
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error: '7z' command failed or not found. {e}")
                return False
    except Exception as e:
        print(f"Detailed error unpacking {archive_path}: {e}")
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
