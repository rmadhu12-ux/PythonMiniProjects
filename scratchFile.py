from MiniProject.client import retry
import httpx

calls = 0

@retry(times=3)
def flaky():
    global calls
    calls += 1
    if calls < 3:
        raise httpx.ReadTimeout("Flaky function failed")
    return "Ok"

for i in range(5):
    try:
        result = flaky()
        print(result)
    except httpx.ReadTimeout as e:
        print("Failed")