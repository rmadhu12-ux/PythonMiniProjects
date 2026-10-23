import pytest
from pydantic import ValidationError
from MiniProject.models import Todo


def testValidateModel():
    todo = Todo.model_validate({"userId": 1, "id": 1, "title": "Test", "completed": False})
    assert todo.userId == 1
    assert todo.id == 1
    assert todo.title == "Test"
    assert todo.completed == False

def testInvalidModel():
    with pytest.raises(Exception):
        Todo.model_validate({"userId": "1", "id": "ax", "title": "Test", "completed": False})