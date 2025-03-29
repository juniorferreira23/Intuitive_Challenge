from settings import logger
import requests
from bs4 import BeautifulSoup, Tag
import re
import os
import zipfile

URL_GOV = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
DOWNLOAD_DIR = "./data"
FILENAME_ZIP = "./data/compress_gov"

log = logger(__file__)

def fetch_page(url: str) -> str | None:
    """
    Get the html content of the page

    Args:
        url (str): url you want to get the html content from.

    Returns:
        str: html content
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        log.debug(response.text)
        log.info("Request to the government made successfully")
        return response.text
    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching page {url}: {e}")
        return None


def parse_files(
    html_content: str,
    tag_content: str | None = None,
    class_content: str | None = None,
    target_file: str | None = None,
) -> list[str]:
    """
    Get the download links

    Args:
        html_content (str): Html content.
        tag_content (str, optional): Content to search for in the tag. Defaults to None.
        class_content (str, optional): class that should be searched for in the tag. Defaults to None.
        target_file (str, optional): Type of file to search for, Example: .pdf and .png. Defaults to None.

    Raises:
        ValueError: Error when tag content and class content parameters cannot be used at the same time

    Returns:
        list[str]: list of links
    """
    if tag_content and class_content:
        raise ValueError(
            "Error when tag content and class content parameters cannot be used at the same time"
        )

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        file_links: list[str] = []

        if tag_content:
            for link in soup.find_all(
                "a", string=re.compile(tag_content, re.IGNORECASE)
            ):
                if isinstance(link, Tag):
                    href = link.get("href")
                    if isinstance(href, str):
                        file_links.append(href)
        elif class_content:
            for link in soup.find_all(
                "a", class_=re.compile(class_content, re.IGNORECASE)
            ):
                if isinstance(link, Tag):
                    href = link.get("href")
                    if isinstance(href, str):
                        file_links.append(href)

        if target_file:
            file_links = [link for link in file_links if link.endswith(target_file)]
        log.debug(file_links)
        log.info("Links successfully fetched")
        return file_links
    except ValueError as e:
        log.error(e)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
    return []


def dowload_file(file_url: str, download_dir: str) -> None:
    """
    Download from the provided url

    Args:
        file_url (str): download url
        download_dir (str): internal folder for storage
    """
    try:
        local_filename = os.path.join(download_dir, file_url.split("/")[-1])
        with requests.get(file_url, stream=True) as r:
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        log.error(f"Unexpected error: {e}")


def compress_file(download_dir: str, filename_zip: str) -> None:
    """
    Compress files within a folder

    Args:
        download_dir (str): folder of files that will be compressed
        filename_zip (str): zip file name
    """
    path = os.path.join(download_dir)
    files = os.listdir(path)
    if not files:
        log.error("Empty file list")
        return None
    files = [os.path.join(download_dir, file) for file in files]
    log.debug(files)
    with zipfile.ZipFile(filename_zip, "w") as zip:
        for file in files:
            zip.write(file, arcname=file)


def main(url: str = URL_GOV, download_dir: str = DOWNLOAD_DIR, filename_zip: str = FILENAME_ZIP):
    html_content = fetch_page(url)
    if not html_content:
        return
    file_links = parse_files(html_content, tag_content=".*Anexo*.", target_file=".pdf")
    if not file_links:
        return
    os.makedirs(download_dir, exist_ok=True)
    for file_link in file_links:
        dowload_file(file_link, download_dir)
    compress_file(download_dir, filename_zip)


if __name__ == "__main__":
    main()
