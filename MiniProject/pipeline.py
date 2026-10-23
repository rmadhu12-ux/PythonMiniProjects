from .client import makeClient, fetchTodos
from .models import Todo
import logging
from pydantic import ValidationError 
from pathlib import Path
import json

logger = logging.getLogger(__name__)

def run(userId, outDir="data"):
    with makeClient() as c:
        details = fetchTodos(c, userId)

    valid, invalid = [], 0
    for item in details:
        try:
            todo = Todo.model_validate(item) #returns todo obj
        except ValidationError as e:
            logger.warning("skipping todo %s: %s", item.get("id"), e)
            invalid += 1
        else:
            valid.append(todo.model_dump()) #modeldump returns dict

    completed = sum(1 for t in valid if t["completed"])
    summary = {
    "userId": userId,
    "fetched": len(details),
    "valid": len(valid),
    "invalid": invalid,
    "completed": completed,
    "pending": len(valid) - completed,
    }

    out = Path(outDir)
    out.mkdir(parents=True, exist_ok=True)
    
    with open(out / f"todos_{userId}.json", "w", encoding="utf-8") as f:
        json.dump(valid, f, indent=2)
    with open(out / f"summary_{userId}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # log: fetched N, valid N, completed N
    logger.info("fetched %d, valid %d, completed %d,  invalid %d",
        len(details), len(valid), completed, invalid)

    return summary

    