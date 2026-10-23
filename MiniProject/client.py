import time
import logging
import functools

import httpx

logger = logging.getLogger(__name__)

def makeClient():
     client = httpx.Client(base_url="https://jsonplaceholder.typicode.com", timeout=5.0)
     return client

def isTransient(e):
    if isinstance(e, (httpx.TimeoutException, httpx.ConnectError)):
        return True
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        return code == 429 or code >= 500
    return False

def retry(times, delay=0.5):
    def decorator(func):
        @functools.wraps(func) 
        def inner(*args, **kwargs):
            for attempt in range (1, times+1):
                    try:
                        return func(*args, **kwargs) 
                    except Exception as e:
                        if not isTransient(e) or attempt == times:
                            raise
                        wait = delay * 2 ** (attempt - 1)
                        logger.warning(
                            "attempt %d failed: %s, retrying in %.1fs", attempt, e, wait
                        )
                        time.sleep(wait)
        return inner
    return decorator

@retry(times = 3)
def fetchTodos(client, userId):
    r = client.get("/todos", params={"userId": userId})
    r.raise_for_status()    
    return r.json()