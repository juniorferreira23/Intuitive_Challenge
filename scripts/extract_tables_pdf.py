import os
from settings import logger
import pdfplumber
import pandas as pd
from utils.file_handler import compress_file

log = logger(__file__)

DIR_DATA = "./data"
PATH_FILE = f"{DIR_DATA}/Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"
FILENAME_ZIP = "./data/tables_ans"


def extract_tables_pdf(
    pdf_path: str, output_file: str, replace_column_names: dict[str, str]
) -> None:
    # TODO: estudar se posso melhorar o desempenho e ver se consigo usar a lib polar para aumentar performance
    """
    Extract tables from pdf

    Args:
        pdf_path (str): file path
        output_file (str): file output path
    """
    try:
        list_tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)
                    list_tables.append(df)
                    log.debug(df)

        end_df = pd.concat(list_tables, ignore_index=True)
        end_df.columns = end_df.iloc[0]
        end_df = end_df[1:].reset_index(drop=True)
        end_df = end_df.rename(columns=replace_column_names)
        end_df.to_csv(output_file, index=False, header=True)
        log.info("Tables extracted successfully")
    except Exception as e:
        log.error(e)


def main(
    dir_data: str = DIR_DATA,
    path_doc_extract: str = PATH_FILE,
    filename_zip: str = FILENAME_ZIP,
):
    os.makedirs(dir_data, exist_ok=True)
    extract_tables_pdf(
        path_doc_extract,
        f"{dir_data}/tables_ans.csv",
        {"OD": "Seg. Odontológica", "AMB": "Seg. Ambulatorial"},
    )
    compress_file(dir_data, filename_zip, [".csv"])


if __name__ == "__main__":
    main()
