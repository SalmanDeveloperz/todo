"""
SQLAlchemy is an ORM, which is Object Relational Mapping
which is what our FASTAPI Application is going to be able to create a database and be able to
create a connection
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db'  # for sqlite connection
#SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:salman123@localhost/TodoApplicationDatabase' #for postgreSQL Connection
SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:salman123@127.0.0.1:3306/TodoApplicationDatabase' #for MySQL connection

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


