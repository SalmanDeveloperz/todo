from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos

app= FastAPI()

models.Base.metadata.create_all(bind=engine) # this only run if todos.db not exist
app.include_router(auth.router)
app.include_router(todos.router)
