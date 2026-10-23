from unittest import result

import httpx
import pytest
from MiniProject.client import isTransient
from MiniProject.client import retry
import MiniProject.client as client_mod

def status_error(code):
    request = httpx.Request("GET", "http://test")
    response = httpx.Response(code, request=request)
    return httpx.HTTPStatusError("boom", response=response, request=request)

@pytest.mark.parametrize("error, expected", [
    (httpx.ReadTimeout("t"), True),
    (httpx.ConnectError("c"), True),
    (status_error(503), True),
    (status_error(429), True),
    (status_error(404), False),
    (status_error(400), False),
    (ValueError("x"), False),
])

def test_is_transient(error, expected):
    assert isTransient(error) is expected


def test_retry_succeeds_after_failures(monkeypatch):
    calls = 0
    monkeypatch.setattr(client_mod.time, "sleep", lambda s: None)
    @retry(times=3)
    def flaky():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise httpx.ReadTimeout("Flaky function failed")
        return "Ok"
    result = flaky()
    assert result == "Ok"
    assert calls == 3


def test_retry_gives_up_after_max_attempts(monkeypatch):
    calls = 0
    waits = []
    monkeypatch.setattr(client_mod.time, "sleep", lambda s: None)
    @retry(times=3)
    def flaky():
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("Flaky function failed")

    with pytest.raises(httpx.ReadTimeout):
        flaky()
    assert calls == 3

def test_no_retries(monkeypatch):
    calls = 0
    monkeypatch.setattr(client_mod.time, "sleep", lambda s: None)
    @retry(times=3)
    def flaky():
        nonlocal calls
        calls += 1
        raise status_error(404)
  
    with pytest.raises(httpx.HTTPStatusError):
        flaky()
    assert calls == 1


def test_retry_backoff_doubles(monkeypatch):
    calls = 0
    waits = []
    monkeypatch.setattr(client_mod.time, "sleep", lambda s: waits.append(s))

    @retry(times=3, delay=0.5)
    def always_times_out():
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("Flaky function failed")

    with pytest.raises(httpx.ReadTimeout):
        always_times_out()

    print(waits) #python -m pytest -s -v -k backoff
    assert waits == [0.5, 1.0]