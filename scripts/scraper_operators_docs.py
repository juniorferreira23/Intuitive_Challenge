from settings import logger, DIR_DATA
from utils.scraper import Scraper
import os
from utils.file_handler import unzip_file

log = logger(__file__)
scraper = Scraper(log)


URLS = [
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2024/",
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2023/",
    "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/",
]


def main(
    urls: str = URLS,
    dir_data: str = DIR_DATA,
):
    for url in urls:
        html_content = scraper.fetch_page(url)
        if not html_content:
            return
        if "demonstracoes" in url:
            type_file = ".zip"
        elif "operadoras" in url:
            type_file = ".csv"
        file_links = scraper.parse_files(html_content, target_file=type_file)
        if not file_links:
            return
        os.makedirs(dir_data, exist_ok=True)
        for file_link in file_links:
            scraper.dowload_file(f"{url}{file_link}", dir_data)
            if type_file == ".zip":
                unzip_file(f"{dir_data}/{file_link}", dir_data)
                os.remove(f"{dir_data}/{file_link}")


if __name__ == "__main__":
    main()
