import sys
import pathlib
import copy

# Ensure src is importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import app as app_mod
from fastapi.testclient import TestClient

client = TestClient(app_mod.app)


def setup_function():
    # snapshot activities and restore after each test
    app_mod._activities_backup = copy.deepcopy(app_mod.activities)


def teardown_function():
    app_mod.activities = app_mod._activities_backup
    del app_mod._activities_backup


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Drama Club" in data
    assert isinstance(data["Drama Club"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Drama Club"
    email = "testuser@example.com"

    # ensure not present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"

    # verify added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Unregistered {email} from {activity}"

    # verify removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
