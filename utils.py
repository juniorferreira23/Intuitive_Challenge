import os
from settings import logger
import zipfile

log = logger(__file__)


def compress_file(file_dir: str, filename_zip: str, file_types: list = None) -> None:
    """
    Compress files within a folder based on specified file types

    Args:
        file_dir (str): Folder of files that will be compressed
        filename_zip (str): Zip file name
        file_types (list, optional): List of file extensions to compress (e.g., ['.txt', '.jpg']). Compress all if None.
    """
    path = os.path.join(file_dir)
    files = os.listdir(path)
    if not files:
        log.error("Empty file list")
        return None

    if file_types:
        files = [
            file for file in files if os.path.splitext(file)[1].lower() in file_types
        ]

    if not files:
        log.error("No files matched the specified types")
        return None

    files = [os.path.join(file_dir, file) for file in files]
    log.debug(f"Files to be compressed: {files}")

    with zipfile.ZipFile(filename_zip, "w") as zip:
        for file in files:
            zip.write(file, arcname=os.path.relpath(file, file_dir))
