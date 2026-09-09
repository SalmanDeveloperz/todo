from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from todoApp.models import Todos
from todoApp.database import SessionLocal
from starlette import status

router= APIRouter()

def get_db():
    db=SessionLocal()
    try:
        yield db #yield means the code prior to and including yield
        # statement will execute before sending response

    finally:
        db.close() #this only executed after response has been delivered,
        # make fastAPI quicker, very safe ,close connection in the end

db_dependency= Annotated[Session, Depends(get_db)] #Depends is dependency injection
        # really need before we execute behind scenes

class ToDoRequest(BaseModel):
    title: str = Field(min_length=3)
    description:str = Field(min_length=3, max_length=120)
    owner_id: int = Field(gt=-1 , lt=4)
    complete: bool




# To read all todos
@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(db:db_dependency):
    return db.query(Todos).all()

# To read one specific todo
@router.get("/todos/{todos_id}", status_code=status.HTTP_200_OK)
async def search_specific_todo(db:db_dependency, todos_id: int = Path(gt=0)):
    todo_model= db.query(Todos).filter(Todos.id==todos_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todos not found')

# To add new todo
@router.post("/todo", status_code = status.HTTP_201_CREATED)
async def add_new_todo(db:db_dependency, new_todo: ToDoRequest):
    todo_model= Todos(**new_todo.model_dump())

    db.add(todo_model) #adding means getting database ready
    db.commit() #flushing at all and to transaction to the database

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency, todo_id: int, todo_request: ToDoRequest ):
    todo_model= db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code= 404, detail='Not found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.owner_id = todo_request.owner_id
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency, todo_id: int=Path(gt=0)):
    todo_model=db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todos).filter(Todos.id==todo_id).delete()
    db.commit()


