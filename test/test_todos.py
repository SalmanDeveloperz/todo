from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..main import app
from ..routers.auth import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check _same_thread": False},
    poolclass = StaticPool
)

TestingSessionLocal= sessionmaker(autocommit= False, autoflush= False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db=TestingSessionLocal()
    try:
        yield db  # yield means the code prior to and including yield
        # statement will execute before sending response

    finally:
        db.close()  # this only executed after response has been delivered,
        # make fastAPI quicker, very safe ,close connection in the end

def override_get_current_user():
    return {'username': 'salman', }
app.dependency_overrides[get_db] = override_get_db