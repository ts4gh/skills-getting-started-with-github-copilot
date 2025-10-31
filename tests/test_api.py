import pytest
from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity: known activity exists
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Chess Club"
    email = "test.user+pytest@example.com"

    # URL-encode activity name for path
    activity_esc = quote(activity, safe="")

    # Ensure clean state: if the test email exists, remove it first
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        resp = client.delete(f"/activities/{activity_esc}/participants", params={"email": email})
        assert resp.status_code == 200

    # Sign up
    resp = client.post(f"/activities/{activity_esc}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Remove participant
    resp = client.delete(f"/activities/{activity_esc}/participants", params={"email": email})
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # Verify participant removed
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic sanity: some known activity exists
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Chess Club"
    email = "testuser+signup@mergington.edu"

    # ensure email not present initially (if present, remove first)
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")

    # Sign up
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Remove participant (cleanup)
    resp = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")


def test_remove_nonexistent_participant():
    activity = "Chess Club"
    email = "nonexistent+xyz@mergington.edu"
    resp = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    # 404 expected for missing participant
    assert resp.status_code == 404
