from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles

from todoApp.models import Base
from todoApp.database import engine
from todoApp.routers import auth, todos
from fastapi.templating import Jinja2Templates

app= FastAPI()

Base.metadata.create_all(bind=engine) # this only run if todos.db not exist

templates = Jinja2Templates(directory= "todoApp/templates")

app.mount("/static", StaticFiles(directory="todoApp/static"), name="static")

@app.get("/")
def test(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
