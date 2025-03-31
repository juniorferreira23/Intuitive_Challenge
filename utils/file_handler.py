import os
from settings import logger
import zipfile

log = logger(__file__)


def get_files(dir_path: str, type_files: list[str] | None = None) -> list[str]:
    """
    get files from a directory

    Args:
        dir_path (str): dir path
        type_files (list[str], optional): type of files you want to search for. Defaults to None.

    Returns:
        list[str]: file list
    """
    path = os.path.join(dir_path)
    files = os.listdir(path)
    if type_files:
        files = [file for file in files if file.split('.')[-1] in type_files]
    return files


def compress_file(file_dir: str, filename_zip: str, file_types: list = None) -> None:
    """
    Compress files within a folder based on specified file types

    Args:
        file_dir (str): Folder of files that will be compressed
        filename_zip (str): Zip file name
        file_types (list, optional): List of file extensions to compress (e.g., ['.txt', '.jpg']). Compress all if None.
    """
    files = get_files(file_dir)
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


def unzip_file(file_dir: str, output_file: str) -> None:
    """
    Unzip file

    Args:
        file_dir (str): Folder of files that will be compressed
        output_file (str): destination directory
    """
    try:
        with zipfile.ZipFile(file_dir, "r") as zip:
            zip.extractall(output_file)
        log.info("File unzipped successfully")
    except Exception as e:
        log.error(e)
