"""Unit tests for the payment processing service."""
import base64
import pickle

import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Payment Processing Service" in resp.data


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_process_happy_path(client):
    resp = client.post("/api/v1/process", json={"items": ["a", "b"]})
    assert resp.status_code == 200
    assert resp.get_json()["result"] == [
        {"index": 0, "value": "a"},
        {"index": 1, "value": "b"},
    ]


def test_process_rejects_non_object(client):
    resp = client.post("/api/v1/process", json=["not", "an", "object"])
    assert resp.status_code == 400


def test_process_rejects_missing_items(client):
    resp = client.post("/api/v1/process", json={"foo": "bar"})
    assert resp.status_code == 400


def test_process_rejects_non_list_items(client):
    resp = client.post("/api/v1/process", json={"items": "nope"})
    assert resp.status_code == 400


def test_process_rejects_oversized_payload(client):
    resp = client.post("/api/v1/process", json={"items": list(range(1000))})
    assert resp.status_code == 400
    assert "max" in resp.get_json()["error"]


def test_process_does_not_deserialize_pickle(client):
    """Regression: a pickle blob must be treated as data, never executed."""
    class Boom:
        def __reduce__(self):
            return (open, ("/tmp/should_not_exist_from_test.txt", "w"))

    blob = base64.b64encode(pickle.dumps(Boom())).decode()
    resp = client.post("/api/v1/process", json={"payload": blob})
    # No 'items' key -> rejected, and crucially: nothing deserialized.
    assert resp.status_code == 400


def test_get_required_env_missing(monkeypatch):
    monkeypatch.delenv("SOME_MISSING_KEY", raising=False)
    with pytest.raises(RuntimeError):
        app_module.get_required_env("SOME_MISSING_KEY")


def test_get_required_env_present(monkeypatch):
    monkeypatch.setenv("SOME_KEY", "value")
    assert app_module.get_required_env("SOME_KEY") == "value"
