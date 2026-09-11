from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from todoApp.database import SessionLocal
from todoApp.models import Users
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # OAuth is more secure then simple fastapi
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

router= APIRouter(
    prefix='/auth',
    tags= ['auth']
)

SECRET_KEY='168ace393e8ef571c4b6affef4ccf6d1178ba376832f5054520959c348c91934'
ALGORITHM= 'HS256'

bcrypt_context= CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class Token(BaseModel):
    access_token:str
    token_model:str

def get_db():
    db=SessionLocal()
    try:
        yield db #yield means the code prior to and including yield statement will executed before sending response

    finally:
        db.close() #this only executed after response has been delivered, make fastAPI quicker, very safe ,close connection in the end

db_dependency= Annotated[Session, Depends(get_db)] #depends is dependency injection really need before we execute behind scenes

templates= Jinja2Templates(directory="todoApp/templates")

### Pages ###

@router.get ("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


### Endpoints ###
def authenticate_user(username:str, password:str, db):
    user= db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode= {'sub': username, 'id': user_id}
    expires= datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm= ALGORITHM)

@router.get("/auth/")
async def get_user():
    return {'user': 'authenticated'}
async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str=payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')

        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


@router.post("/", status_code= status.HTTP_201_CREATED)
async def create_user( db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model=Users(
        email=create_user_request.email,
        username= create_user_request.username,
        first_name= create_user_request.first_name,
        last_name= create_user_request.last_name,
        role= create_user_request.role,
        hashed_password= bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number= create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()



@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db:db_dependency):
    user= authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
