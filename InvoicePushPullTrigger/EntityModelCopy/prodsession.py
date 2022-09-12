from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os



PWD=os.getenv('DATABASE_PASS',default='ehgProd2022!')
USR=os.getenv('DATABASE_USER',default='ehg_user')
HOST = os.getenv('DATABASE_HOST',default="agiprod.mysql.database.azure.com")
PORT = os.getenv('DATABASE_PORT',default='3306')
DB = os.getenv('DATABASE_DB',default='rove_hotels')

SQLALCHEMY_DATABASE_URL = f'mysql://{USR}:{PWD}@{HOST}:{PORT}/{DB}'
# SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{SQL_USER}:{SQL_PASS}@{localhost}:{SQL_PORT}/{SQL_DB}'

prodengine1 = create_engine(
    SQLALCHEMY_DATABASE_URL
)
prodengine = create_engine(f'mysql+pymysql://{USR}:{PWD}@{HOST}:{PORT}/{DB}')



ProdSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=prodengine))
ProdBase = declarative_base()



