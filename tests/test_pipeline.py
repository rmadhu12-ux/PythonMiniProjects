import httpx
import pytest
import MiniProject.pipeline as pipeline
from tests.conftest import sample_items
from MiniProject.client import retry
import json
import MiniProject.client as client_mod

def test_run_success(monkeypatch, tmp_path, sample_items):
    def handler(request):
        return httpx.Response(200, json=sample_items)

    def fakeClient():
        return httpx.Client(
            base_url="http://fake-test", 
            transport=httpx.MockTransport(handler))
    
    monkeypatch.setattr(pipeline, "makeClient", fakeClient)

    summary = pipeline.run(1, tmp_path)

    assert summary["fetched"] == 3
    assert summary["valid"] == 2
    assert summary["invalid"] == 1
    assert summary["completed"] == 1
    assert (tmp_path / "summary_1.json").exists()
    saved = json.loads((tmp_path / "todos_1.json").read_text())   
    assert len(saved) == 2

def test_retry_503_success(monkeypatch, tmp_path, sample_items):
    calls = []
    def handler(request):
        calls.append(1)
        return httpx.Response(503)

    def fakeClient():
        return httpx.Client(
            base_url="http://fake-test", 
            transport=httpx.MockTransport(handler))
    
    monkeypatch.setattr(pipeline, "makeClient", fakeClient)
    monkeypatch.setattr(client_mod.time, "sleep", lambda s: None)

    with pytest.raises(httpx.HTTPStatusError):
        pipeline.run(1, tmp_path)

    assert len(calls) == 3
    assert not (tmp_path / "summary_1.json").exists()

def test_no_retry_404(monkeypatch, tmp_path, sample_items):
    calls = []
    def handler(request):
        calls.append(1)
        return httpx.Response(404)

    def fakeClient():
        return httpx.Client(
            base_url="http://fake-test", 
            transport=httpx.MockTransport(handler))
    
    monkeypatch.setattr(pipeline, "makeClient", fakeClient)
    monkeypatch.setattr(client_mod.time, "sleep", lambda s: None)

    with pytest.raises(httpx.HTTPStatusError):
        pipeline.run(1, tmp_path)

    assert len(calls) == 1
    assert not (tmp_path / "summary_1.json").exists()