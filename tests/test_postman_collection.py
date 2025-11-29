import json
import os
import sys
from fastapi.testclient import TestClient

# ensure local project "app" package is used
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
import types
import importlib.util

# ensure full app package hierarchy is in sys.modules BEFORE loading any modules
app_pkg = types.ModuleType("app")
app_pkg.__path__ = [os.path.join(ROOT, "app")]
sys.modules["app"] = app_pkg

app_api_pkg = types.ModuleType("app.api")
app_api_pkg.__path__ = [os.path.join(ROOT, "app", "api")]
sys.modules["app.api"] = app_api_pkg

app_api_v1_pkg = types.ModuleType("app.api.v1")
app_api_v1_pkg.__path__ = [os.path.join(ROOT, "app", "api", "v1")]
sys.modules["app.api.v1"] = app_api_v1_pkg

app_api_v1_endpoints_pkg = types.ModuleType("app.api.v1.endpoints")
app_api_v1_endpoints_pkg.__path__ = [os.path.join(ROOT, "app", "api", "v1", "endpoints")]
sys.modules["app.api.v1.endpoints"] = app_api_v1_endpoints_pkg

app_db_pkg = types.ModuleType("app.db")
app_db_pkg.__path__ = [os.path.join(ROOT, "app", "db")]
sys.modules["app.db"] = app_db_pkg

app_core_pkg = types.ModuleType("app.core")
app_core_pkg.__path__ = [os.path.join(ROOT, "app", "core")]
sys.modules["app.core"] = app_core_pkg

app_services_pkg = types.ModuleType("app.services")
app_services_pkg.__path__ = [os.path.join(ROOT, "app", "services")]
sys.modules["app.services"] = app_services_pkg

# attach child packages
sys.modules["app"].api = sys.modules["app.api"]
sys.modules["app"].db = sys.modules["app.db"]
sys.modules["app"].core = sys.modules["app.core"]
sys.modules["app"].services = sys.modules["app.services"]
sys.modules["app.api"].v1 = sys.modules["app.api.v1"]
sys.modules["app.api.v1"].endpoints = sys.modules["app.api.v1.endpoints"]

# Now load api.py which uses relative imports like from .v1.endpoints
API_PATH = os.path.join(ROOT, "app", "api", "api.py")
spec = importlib.util.spec_from_file_location("app.api", API_PATH)
api_module = importlib.util.module_from_spec(spec)
api_module.__package__ = "app.api"
sys.modules["app.api"] = api_module
spec.loader.exec_module(api_module)

from bson import ObjectId

CLIENT = TestClient(api_module.app)

COL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "postman_collection.json"))

with open(COL_PATH, "r", encoding="utf-8") as f:
    COLLECTION = json.load(f)


# Helper to stub repository functions
def _set_basic_stubs():
    """Set default repository behavior for tests (successful flow)."""
    from app.db.repositories import user_repo, community_repo, user_community_repo, message_repo

    # basic fake user and community ids
    fake_uid = str(ObjectId())
    fake_cid = str(ObjectId())

    # stub users
    user_repo.get_user_by_email = lambda email: {"_id": fake_uid, "email": email, "password": "password1"}
    user_repo.create_user = lambda data: {**data, "_id": fake_uid}
    user_repo.get_user_by_id = lambda uid: {"_id": uid, "email": "x@y.z"}

    # stub communities
    community_repo.create_community = lambda data: {**data, "_id": fake_cid}
    community_repo.get_community_by_id = lambda cid: {"_id": cid, "name": "test", "owner": fake_uid}
    community_repo.update_community = lambda cid, u: {**{"_id": cid}, **u}
    community_repo.delete_community = lambda cid: True

    # stub memberships
    user_community_repo.join_community = lambda uid, cid, role="member": {"_id": str(ObjectId()), "uid": uid, "cid": cid, "role": role}
    user_community_repo.leave_community = lambda uid, cid: True
    user_community_repo.is_member = lambda uid, cid: True

    # stub messages
    message_repo.count_recent_messages_by_user = lambda u, c, seconds=60: 0
    message_repo.create_message = lambda data: {**data, "_id": str(ObjectId())}
    message_repo.list_messages_by_community = lambda cid, limit=100: []


def test_collection_requests():
    # prep stubs for happy path
    _set_basic_stubs()

    for item in COLLECTION.get("item", []):
        name = item.get("name")
        req = item.get("request", {})
        method = req.get("method")

        # build URL path
        raw = req.get("url", {}).get("raw", "")
        path = raw.replace("{{baseUrl}}", "").strip()
        if path.startswith("http://") or path.startswith("https://"):
            if "/" in path[8:]:
                path = "/" + path.split("/", 3)[3]
            else:
                path = "/"

        # headers
        headers = {h["key"]: h["value"] for h in req.get("header", [])}
        token = headers.get("Authorization", "").replace("Bearer ", "")
        if token and token.strip() == "{{testUserToken}}":
            headers["Authorization"] = f"Bearer {str(ObjectId())}"

        # body
        body_raw = None
        if req.get("body") and req["body"].get("mode") == "raw":
            body_raw = req["body"].get("raw")
            body_raw = body_raw.replace("{{testUserId}}", str(ObjectId()))
            body_raw = body_raw.replace("{{testCommunityId}}", str(ObjectId()))

        # perform request
        if method == "GET":
            r = CLIENT.get(path, headers=headers)
        elif method == "POST":
            if headers.get("Content-Type", "") == "application/json":
                r = CLIENT.post(path, headers=headers, data=body_raw if body_raw else None)
            else:
                r = CLIENT.post(path, headers=headers)
        elif method == "PUT":
            r = CLIENT.put(path, headers=headers, data=body_raw if body_raw else None)
        elif method == "DELETE":
            r = CLIENT.delete(path, headers=headers)
        else:
            r = None

        assert r is not None, f"request for {name} returned None"
        assert r.status_code < 500, f"{name} failed with status {r.status_code} and body {r.text}"
