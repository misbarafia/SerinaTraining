from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os



PWD=os.getenv('DATABASE_PASS',default='dsserina')
USR=os.getenv('DATABASE_USER',default='serina')
HOST = os.getenv('DATABASE_HOST',default="serina-qa-server1.mysql.database.azure.com")
PORT = os.getenv('DATABASE_PORT',default='3306')
DB = os.getenv('DATABASE_DB',default='rove_hotels')


SQLALCHEMY_DATABASE_URL = f'mysql://{USR}:{PWD}@{HOST}:{PORT}/{DB}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)


Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
