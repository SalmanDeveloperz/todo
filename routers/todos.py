from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from todoApp.models import Todos
from todoApp.database import SessionLocal
from starlette import status
from todoApp.routers.auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

def get_db():
    db=SessionLocal()
    try:
        yield db #yield means the code prior to and including yield
        # statement will execute before sending response

    finally:
        db.close() #this only executed after response has been delivered,
        # make fastAPI quicker, very safe ,close connection in the end

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
templates = Jinja2Templates(directory="todoApp/templates")

class ToDoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: str = Field(min_length=3, max_length=240)
    complete: bool = False




# To read all todos
@router.get("/todo-page")
async def render_todo_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@router.get("", status_code=status.HTTP_200_OK)
async def read_all_todos(db: db_dependency, current_user: user_dependency):
    return db.query(Todos).filter(Todos.owner_id == current_user["id"]).order_by(Todos.id.desc()).all()

# To read one specific todo
@router.get("/{todos_id}", status_code=status.HTTP_200_OK)
async def search_specific_todo(db: db_dependency, current_user: user_dependency, todos_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(
        Todos.id == todos_id, Todos.owner_id == current_user["id"]
    ).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

# To add new todo
@router.post("", status_code=status.HTTP_201_CREATED)
async def add_new_todo(db: db_dependency, current_user: user_dependency, new_todo: ToDoRequest):
    todo_model = Todos(**new_todo.model_dump(), owner_id=current_user["id"])
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

@router.put("/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(db: db_dependency, current_user: user_dependency, todo_id: int, todo_request: ToDoRequest):
    todo_model = db.query(Todos).filter(
        Todos.id == todo_id, Todos.owner_id == current_user["id"]
    ).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.complete = todo_request.complete
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, current_user: user_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(
        Todos.id == todo_id, Todos.owner_id == current_user["id"]
    ).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()


