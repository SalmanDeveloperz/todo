"""
SQLAlchemy is an ORM, which is Object Relational Mapping
which is what our FASTAPI Application is going to be able to create a database and be able to
create a connection
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"mysql+pymysql://root:salman123@127.0.0.1:3306/TodoApplicationDatabase?charset=utf8mb4",
)

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
	SQLALCHEMY_DATABASE_URL,
	connect_args=connect_args,
	pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


