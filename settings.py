import os
import logging
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_DATA = "./data"

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def logger(file_name: str) -> logging.Logger:
    log_dir = os.path.join(ROOT_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    file_name = os.path.splitext(os.path.basename(file_name))[0]

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, f"{file_name}.log")),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(file_name)
