from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DIALECT = "mysql"
DRIVER = "pymysql"
PORT = 3306
DATABASE = "db"
HOST = "localhost"
USER = "user"
PASSWORD = "password"


def SQLALCHEMY_DATABASE_URI():
    return "{}+{}://{}:{}@{}:{}/{}".format(
        DIALECT, DRIVER, USER, PASSWORD, HOST, PORT, DATABASE,
    )


connection_config = {"timeout": 10, "retries": 10, "parallel_max": 10}

engine = create_engine(SQLALCHEMY_DATABASE_URI())
base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)
db_session = Session()
