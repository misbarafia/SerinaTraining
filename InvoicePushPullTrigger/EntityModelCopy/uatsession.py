from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os,pymysql
pymysql.install_as_MySQLdb()



PWD=os.getenv('DATABASE_PASS',default='dsserina')
USR=os.getenv('DATABASE_USER',default='serina')
HOST = os.getenv('DATABASE_HOST',default="serina-qa-server1.mysql.database.azure.com")
PORT = os.getenv('DATABASE_PORT',default='3306')
DB = os.getenv('DATABASE_DB',default='rove_hotels_uat')

SQLALCHEMY_DATABASE_URL = f'mysql://{USR}:{PWD}@{HOST}:{PORT}/{DB}'
# SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{SQL_USER}:{SQL_PASS}@{localhost}:{SQL_PORT}/{SQL_DB}'

uatengine1 = create_engine(
    SQLALCHEMY_DATABASE_URL
)
uatengine = create_engine(f'mysql+pymysql://{USR}:{PWD}@{HOST}:{PORT}/{DB}')



UATSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=uatengine))
UATBase = declarative_base()



