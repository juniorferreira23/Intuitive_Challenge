from settings import logger, DIR_DATA
from utils.scraper import Scraper
import os
from utils.file_handler import compress_file

log = logger(__file__)
scraper = Scraper(log)

URL_GOV = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
FILENAME_ZIP = "./data/compress_gov"


def main(
    url: str = URL_GOV,
    dir_data: str = DIR_DATA,
    filename_zip: str = FILENAME_ZIP,
):
    html_content = scraper.fetch_page(url)
    if not html_content:
        return
    file_links = scraper.parse_files(
        html_content, tag_content=".*Anexo*.", target_file=".pdf"
    )
    if not file_links:
        return
    os.makedirs(dir_data, exist_ok=True)
    for file_link in file_links:
        scraper.dowload_file(file_link, dir_data)
    compress_file(dir_data, filename_zip, [".pdf"])


if __name__ == "__main__":
    main()
