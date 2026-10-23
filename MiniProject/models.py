from pydantic import BaseModel

#Validate the response with Pydantic
class Todo(BaseModel):
    userId: int
    id: int
    title: str
    completed: bool