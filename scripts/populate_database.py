from settings import logger, DIR_DATA, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER
import pymysql
from pymysql.cursors import Cursor
import pandas as pd
from utils.file_handler import get_files
import numpy as np

log = logger(__file__)

IGNORE_FILES = ["Relatorio_cadop.csv", "tables_ans.csv"]

QUERY1 = """
    -- 10 operadoras com maiores despesas no último trimestre
    SELECT 
        o.razao_social,
        o.nome_fantasia,
        SUM(d.vl_saldo_final) AS total_despesas
    FROM 
        demonstracoes_contabeis d
    JOIN 
        operadoras o ON d.reg_ans = o.registro_ans
    WHERE 
        d.descricao LIKE '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSIST%'
        AND d.data >= DATE_SUB(
            (SELECT MAX(data) FROM demonstracoes_contabeis), 
            INTERVAL 3 MONTH
        )
    GROUP BY 
        o.razao_social, o.nome_fantasia
    HAVING 
        total_despesas > 0
    ORDER BY 
        total_despesas DESC
    LIMIT 10;
"""

QUERY2 = """
    -- 10 operadoras com maiores despesas no último ano
    WITH ultimo_ano AS (
        SELECT 
            DATE_FORMAT(DATE_SUB(MAX(data), INTERVAL 1 YEAR), '%Y-01-01') AS inicio_ano,
            DATE_FORMAT(MAX(data), '%Y-12-31') AS fim_ano
        FROM demonstracoes_contabeis
    )
    SELECT 
        o.razao_social,
        o.nome_fantasia,
        SUM(d.vl_saldo_final) AS total_despesas
    FROM 
        demonstracoes_contabeis d
    JOIN 
        operadoras o ON d.reg_ans = o.registro_ans
    JOIN 
        ultimo_ano p
    WHERE 
        d.descricao LIKE '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSIST%'
        AND d.data >= p.inicio_ano
        AND d.data <= p.fim_ano
    GROUP BY 
        o.razao_social, o.nome_fantasia
    HAVING 
        total_despesas > 0
    ORDER BY 
        total_despesas DESC
    LIMIT 10;
    
"""


def create_db(cursor: Cursor, db_name: str) -> None:
    """
    Creates the operator and accounting statement tables of a database

    Args:
        cursor (Cursor): an instance of courses from the db connection lib
        db_name (str): database name

    """
    try:
        schema_sql = [
            f"CREATE DATABASE IF NOT EXISTS {db_name};",
            f"USE {db_name};",
            """CREATE TABLE IF NOT EXISTS operadoras (
                registro_ans VARCHAR(20) PRIMARY KEY,
                cnpj VARCHAR(14),
                razao_social VARCHAR(255),
                nome_fantasia VARCHAR(255),
                modalidade VARCHAR(100),
                logradouro VARCHAR(255),
                numero VARCHAR(20),
                complemento VARCHAR(100),
                bairro VARCHAR(100),
                cidade VARCHAR(100),
                uf VARCHAR(2),
                cep VARCHAR(8),
                ddd VARCHAR(2),
                telefone VARCHAR(20),
                fax VARCHAR(20),
                endereco_eletronico VARCHAR(100),
                representante VARCHAR(255),
                cargo_representante VARCHAR(100),
                Regiao_de_Comercializacao VARCHAR(100),
                data_registro_ans DATE
            );""",
            """CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
                id SERIAL PRIMARY KEY,
                data DATE,
                reg_ans VARCHAR(20),
                cd_conta_contabil VARCHAR(50),
                descricao TEXT,
                vl_saldo_inicial DECIMAL(15,2),
                vl_saldo_final DECIMAL(15,2),
                FOREIGN KEY (reg_ans) REFERENCES operadoras(registro_ans)
            );""",
        ]

        for query in schema_sql:
            cursor.execute(query)

        log.info(f"Database {db_name} created sucessfully")
    except Exception as e:
        raise Exception(e)


def extract_data(file_path: str) -> pd.DataFrame:
    """
    extract data from csv file

    Args:
        file_path (str): file path

    Raises:
        Exception: Error in extract_data

    Returns:
        pd.DataFrame: DataFrame
    """
    try:
        df = pd.read_csv(
            file_path,
            sep=";",
            decimal=",",
            quotechar='"',
            dtype=str,
            encoding="utf-8",
        )
        return df
    except Exception as e:
        log.error("Error in extract_data: {str(e)}")
        raise Exception(e)


def transform_data(df: pd.DataFrame, value_columns: list[str]) -> pd.DataFrame:
    """
    Formats dataframe data

    Args:
        df (pd.DataFrame): DataFrame
        value_columns (list[str]): Receives a list of column names of real values ​​to swap "," or "."

    Raises:
        Exception: Error in transform_data

    Returns:
        pd.DataFrame: _description_
    """
    try:
        if value_columns:
            for col in value_columns:
                if col not in df.columns:
                    continue
                df[col] = df[col].str.replace(".", "", regex=False)
                df[col] = df[col].str.replace(",", ".", regex=False)
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "DATA" in df.columns:
            df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce").dt.strftime(
                "%Y-%m-%d"
            )

        df = df.replace({np.nan: None})

        return df
    except Exception as e:
        log.error(f"Error in transform_data: {str(e)}")
        raise Exception(e)


def load_in_db(cursor: Cursor, df: pd.DataFrame, table_name: str) -> None:
    """_summary_

    Args:
        cursor (Cursor): an instance of courses from the db connection lib
        df (pd.DataFrame): DataFrame
        table_name (str): table name in db

    Raises:
        Exception: Error in load_in_db
    """
    try:
        if table_name == "demonstracoes_contabeis":
            cursor.execute("SELECT registro_ans FROM operadoras")
            registros_validos = {row["registro_ans"] for row in cursor.fetchall()}

            df = df[df["REG_ANS"].isin(registros_validos)]
            log.info(f"Filtered {len(df)} valid records for table {table_name}")

        if df.empty:
            log.warning(f"No valid records to insert into {table_name}. Skipping.")
            return

        columns = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        data = [tuple(x) for x in df.to_numpy()]
        cursor.executemany(query, data)
    except Exception as e:
        raise Exception(f"Error in load_in_db: {str(e)}")


def etl(
    cursor: Cursor,
    file_path: str,
    table_name: str,
    value_columns: list[str] | None = None,
) -> None:
    """_summary_

    Args:
        cursor (Cursor): an instance of courses from the db connection lib
        file_path (str): file path
        table_name (str): table name in db
        value_columns (list[str] | None, optional): Receives a list of column
        names of real values ​​to swap "," or ".". Defaults to None.

    Raises:
        Exception: Error processing file
    """
    try:
        log.info(f"Processing file: {file_path}")
        df = extract_data(file_path)
        df = transform_data(df, value_columns)
        load_in_db(cursor, df, table_name)
        log.info(f"Successfully processed {len(df)} records from {file_path}")
    except Exception as e:
        log.error(f"Error processing file {file_path}: {str(e)}")
        raise Exception(e)


def select_query_db(cursor: Cursor, query: str) -> None:
    """
    Performs select query on the database

    Args:
        cursor (Cursor): an instance of courses from the db connection lib
        query (str): Query.sql
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            print(row)

    except pymysql.MySQLError as e:
        log.error(f"Error performing query: {e}")


def main(
    host: str = DB_HOST,
    user: str = DB_USER,
    password: str = DB_PASSWORD,
    db_name: str = DB_NAME,
) -> None:
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        cursor = conn.cursor()

        create_db(cursor, db_name)
        conn.select_db(db_name)

        etl(cursor, f"{DIR_DATA}/Relatorio_cadop.csv", "operadoras")
        conn.commit()
        files = get_files(DIR_DATA, ["csv"])
        files = [file for file in files if file not in IGNORE_FILES]

        for file in files:
            try:
                etl(
                    cursor,
                    f"{DIR_DATA}/{file}",
                    "demonstracoes_contabeis",
                    ["VL_SALDO_INICIAL", "VL_SALDO_FINAL"],
                )
                conn.commit()
            except Exception as e:
                conn.rollback()
                log.error(f"Failed to process {file}: {str(e)}")
                continue

        log.info("Data added successfully")

        for query in [QUERY1, QUERY2]:
            select_query_db(cursor, query)
            print("=" * 100)
    except Exception as e:
        log.error(f"Main error: {str(e)}")
        if "conn" in locals():
            conn.rollback()
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
