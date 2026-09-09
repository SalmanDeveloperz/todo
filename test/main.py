from fastapi import FastAPI
from todoApp.test.models import Base
from todoApp.test.database import engine
from todoApp.routers import auth, todos

app= FastAPI()

Base.metadata.create_all(bind=engine) # this only run if todos.db not exist

@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
