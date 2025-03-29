import os
import logging

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


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
