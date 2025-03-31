import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

class Database:
    def __init__(self, user:str, password:str, database:str, host:str='localhost', port:str='3306'):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.create_database_if_not_exists()
        self.connection = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    def create_database_if_not_exists(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = connection.cursor()            
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.database}')
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            raise Exception(f'Could not connect to the database: {e}')

    def connect(self) -> None:
        try:
            self.engine = engine = create_engine(self.connection, echo=False)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        except Exception as e:
            print(f'Could not connect to the database: {e}')
                
    def base(self) -> None:
        self.Base = declarative_base()