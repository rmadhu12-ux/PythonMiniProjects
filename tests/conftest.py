import pytest

@pytest.fixture
def sample_items():
    return [
        {"userId": 1, "id": 1, "title": "a", "completed": True},
        {"userId": 1, "id": 2, "title": "b", "completed": False},
        {"id": 999},   # invalid on purpose
    ]