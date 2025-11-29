import sys, os
import pytest

# ensure project root is first on sys.path so 'app' imports our package, not a system module named 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib.util

# import our model modules directly to avoid conflicts with other 'app' top-level modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


message_mod = _load_module(os.path.join(ROOT, 'app', 'db', 'models', 'message.py'), 'message_mod')
user_mod = _load_module(os.path.join(ROOT, 'app', 'db', 'models', 'user.py'), 'user_mod')

MessageIn = message_mod.MessageIn
MessageSchema = message_mod.MessageSchema
UserSchema = user_mod.UserSchema
from datetime import datetime
from bson import ObjectId


def test_message_text_validator_blank():
    with pytest.raises(Exception):
        MessageIn(uid=str(ObjectId()), cid=str(ObjectId()), text="   ")


def test_message_uid_cid_invalid():
    with pytest.raises(Exception):
        MessageIn(uid="notanid", cid="also-not-an-id", text="hey")


def test_message_schema_created_at_default():
    m = MessageSchema(uid=str(ObjectId()), cid=str(ObjectId()), text="hello world")
    assert isinstance(m.created_at, datetime)


def test_user_requires_email_password():
    with pytest.raises(Exception):
        UserSchema(name="abc", role="user")

    u = UserSchema(name="Alice", email="a@x.com", password="password1", role="user")
    assert u.email == "a@x.com"
    assert u.password == "password1"
