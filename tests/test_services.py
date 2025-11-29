import sys, os
import pytest

# force the project root onto sys.path so local "app" package is used instead of any global module named "app"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import importlib.util
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def _load_pkg(name, relpath):
    p = os.path.join(ROOT, relpath)
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Create minimal package hierarchy in sys.modules BEFORE loading any app modules
app_pkg = types.ModuleType("app")
app_pkg.__path__ = [os.path.join(ROOT, "app")]
sys.modules["app"] = app_pkg

app_db_pkg = types.ModuleType("app.db")
app_db_pkg.__path__ = [os.path.join(ROOT, "app", "db")]
sys.modules["app.db"] = app_db_pkg

app_db_models_pkg = types.ModuleType("app.db.models")
app_db_models_pkg.__path__ = [os.path.join(ROOT, "app", "db", "models")]
sys.modules["app.db.models"] = app_db_models_pkg

app_db_repositories_pkg = types.ModuleType("app.db.repositories")
app_db_repositories_pkg.__path__ = [os.path.join(ROOT, "app", "db", "repositories")]
sys.modules["app.db.repositories"] = app_db_repositories_pkg

app_services_pkg = types.ModuleType("app.services")
app_services_pkg.__path__ = [os.path.join(ROOT, "app", "services")]
sys.modules["app.services"] = app_services_pkg

app_services_auth_service_pkg = types.ModuleType("app.services.auth_service")
sys.modules["app.services.auth_service"] = app_services_auth_service_pkg

app_services_user_service_pkg = types.ModuleType("app.services.user_service")
sys.modules["app.services.user_service"] = app_services_user_service_pkg

app_services_chat_service_pkg = types.ModuleType("app.services.chat_service")
sys.modules["app.services.chat_service"] = app_services_chat_service_pkg

app_services_community_service_pkg = types.ModuleType("app.services.community_service")
sys.modules["app.services.community_service"] = app_services_community_service_pkg

app_core_pkg = types.ModuleType("app.core")
app_core_pkg.__path__ = [os.path.join(ROOT, "app", "core")]
sys.modules["app.core"] = app_core_pkg

# attach child packages as attributes on parent packages
sys.modules["app"].db = sys.modules["app.db"]
sys.modules["app"].services = sys.modules["app.services"]
sys.modules["app"].core = sys.modules["app.core"]
sys.modules["app.db"].models = sys.modules["app.db.models"]
sys.modules["app.db"].repositories = sys.modules["app.db.repositories"]

# Now load the modules
_load_pkg("app.core.database", os.path.join("app", "core", "database.py"))
_load_pkg("app.core.config", os.path.join("app", "core", "config.py"))
_load_pkg("app.db.models.user", os.path.join("app", "db", "models", "user.py"))
_load_pkg("app.db.models.message", os.path.join("app", "db", "models", "message.py"))
_load_pkg("app.db.models.community", os.path.join("app", "db", "models", "community.py"))
_load_pkg("app.db.repositories", os.path.join("app", "db", "repositories", "__init__.py"))
_load_pkg("app.services.auth_service", os.path.join("app", "services", "auth_service.py"))
_load_pkg("app.services.user_service", os.path.join("app", "services", "user_service.py"))
_load_pkg("app.services.chat_service", os.path.join("app", "services", "chat_service.py"))
_load_pkg("app.services.community_service", os.path.join("app", "services", "community_service.py"))
_load_pkg("app.services", os.path.join("app", "services", "__init__.py"))

from bson import ObjectId


def test_auth_get_user_id_from_token_valid():
    from app.services import get_user_id_from_token
    objid = str(ObjectId())
    assert get_user_id_from_token(objid) == objid


def test_chat_send_message_invalid_ids():
    from app.services import chat_service
    with pytest.raises(ValueError):
        chat_service.send_message("not-id", "also-not-id", "hello")


def test_chat_send_message_user_not_exist(monkeypatch):
    from app.services import chat_service

    monkeypatch.setattr("app.services.chat_service.user_repo.get_user_by_id", lambda u: None)
    # valid object ids
    uid = str(ObjectId())
    cid = str(ObjectId())
    with pytest.raises(ValueError) as e:
        chat_service.send_message(uid, cid, "hello")
    assert "user does not exist" in str(e.value)


def test_chat_send_message_not_member(monkeypatch):
    from app.services import chat_service

    monkeypatch.setattr("app.services.chat_service.user_repo.get_user_by_id", lambda u: {"_id": u})
    monkeypatch.setattr("app.services.chat_service.community_repo.get_community_by_id", lambda c: {"_id": c})
    monkeypatch.setattr("app.services.chat_service.user_community_repo.is_member", lambda u, c: False)

    uid = str(ObjectId())
    cid = str(ObjectId())
    with pytest.raises(ValueError) as e:
        chat_service.send_message(uid, cid, "hi")
    assert "user is not a member" in str(e.value)


def test_chat_send_message_rate_limit(monkeypatch):
    from app.services import chat_service

    monkeypatch.setattr("app.services.chat_service.user_repo.get_user_by_id", lambda u: {"_id": u})
    monkeypatch.setattr("app.services.chat_service.community_repo.get_community_by_id", lambda c: {"_id": c})
    monkeypatch.setattr("app.services.chat_service.user_community_repo.is_member", lambda u, c: True)
    # simulate many recent messages
    monkeypatch.setattr("app.services.chat_service.message_repo.count_recent_messages_by_user", lambda u, c, seconds: chat_service.MAX_MESSAGES_PER_MINUTE)

    uid = str(ObjectId())
    cid = str(ObjectId())
    with pytest.raises(ValueError) as e:
        chat_service.send_message(uid, cid, "hi")
    assert "rate limit exceeded" in str(e.value)


def test_chat_send_message_success(monkeypatch):
    from app.services import chat_service

    created = {"_id": str(ObjectId()), "uid": str(ObjectId()), "cid": str(ObjectId()), "text": "ok"}
    monkeypatch.setattr("app.services.chat_service.user_repo.get_user_by_id", lambda u: {"_id": u})
    monkeypatch.setattr("app.services.chat_service.community_repo.get_community_by_id", lambda c: {"_id": c})
    monkeypatch.setattr("app.services.chat_service.user_community_repo.is_member", lambda u, c: True)
    monkeypatch.setattr("app.services.chat_service.message_repo.count_recent_messages_by_user", lambda u, c, seconds: 0)
    monkeypatch.setattr("app.services.chat_service.message_repo.create_message", lambda data: created)

    res = chat_service.send_message(created["uid"], created["cid"], "hello")
    assert res == created


def test_update_message_permissions(monkeypatch):
    from app.services import chat_service

    # message authored by user1, community owner owner1
    mid = str(ObjectId())
    user1 = str(ObjectId())
    cid = str(ObjectId())
    msg = {"_id": mid, "uid": user1, "cid": cid, "text": "x"}
    monkeypatch.setattr("app.services.chat_service.message_repo.get_message_by_id", lambda m: msg)
    monkeypatch.setattr("app.services.chat_service.community_repo.get_community_by_id", lambda c: {"_id": c, "owner": "owner1"})
    # author can update
    monkeypatch.setattr("app.services.chat_service.message_repo.update_message", lambda mid, update: {"_id": mid, **update})
    out = chat_service.update_message(mid, user1, "newtext")
    assert out["text"] == "newtext"

    # non-author, non-owner cannot update
    with pytest.raises(PermissionError):
        chat_service.update_message(mid, str(ObjectId()), "x2")


def test_community_create_checks_and_join(monkeypatch):
    from app.services import community_service

    # owner missing
    monkeypatch.setattr("app.services.community_service.user_repo.get_user_by_id", lambda u: None)
    with pytest.raises(ValueError):
        community_service.create_community({"name": "g", "owner": "no"})

    # success path - ensure join_community called
    called = {}

    def fake_create(payload):
        return {"_id": "cid1", **payload}

    def fake_join(uid, cid, role="member"):
        called["joined"] = (uid, cid, role)
        return {"_id": "m1"}

    monkeypatch.setattr("app.services.community_service.user_repo.get_user_by_id", lambda u: {"_id": u})
    monkeypatch.setattr("app.services.community_service.community_repo.create_community", fake_create)
    monkeypatch.setattr("app.services.community_service.user_community_repo.join_community", fake_join)

    res = community_service.create_community({"name": "G", "owner": "u1", "description": "d"})
    assert res["_id"] == "cid1"
    assert called["joined"][0] == "u1"
