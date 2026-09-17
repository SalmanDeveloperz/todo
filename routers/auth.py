import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from todoApp.database import SessionLocal
from todoApp.models import Users

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="todoApp/templates")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret-before-deploying")
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    email: str = Field(min_length=5, max_length=120)
    first_name: str = Field(min_length=1, max_length=40)
    last_name: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=8, max_length=72)
    role: str = Field(default="member", max_length=30)
    phone_number: str = Field(default="", max_length=30)


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if user is None or not user.is_active:
        return None
    try:
        return user if bcrypt_context.verify(password, user.hashed_password) else None
    except ValueError:
        return None


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    payload = {
        "sub": username,
        "id": user_id,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_bearer)],
):
    token = token or request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if not username or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return {"username": username, "id": int(user_id)}
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid authentication token")


@router.get("/me")
async def read_current_user(current_user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    user = db.query(Users).filter(Users.id == current_user["id"], Users.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return {"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name, "email": user.email}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, request: CreateUserRequest):
    existing = db.query(Users).filter((Users.username == request.username) | (Users.email == request.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already exists")
    user = Users(
        username=request.username,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role,
        phone_number=request.phone_number,
        hashed_password=bcrypt_context.hash(request.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    return {"message": "Account created"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {
        "access_token": create_access_token(user.username, user.id, timedelta(hours=1)),
        "token_type": "bearer",
    }
