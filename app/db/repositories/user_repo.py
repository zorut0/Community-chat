from typing import Optional, Dict, Any, List
from bson import ObjectId
from ...db.models.user import UserSchema
from ...core.database import get_db

db = get_db()
users_coll = db.users


def create_user(data: Dict[str, Any]) -> Dict:
    # Here 'data' should conform to UserSchema but repository accepts dict.
    result = users_coll.insert_one(data)
    return users_coll.find_one({'_id': result.inserted_id})


def get_user_by_id(user_id: str) -> Optional[Dict]:
    if not ObjectId.is_valid(user_id):
        return None
    return users_coll.find_one({'_id': ObjectId(user_id)})


def get_user_by_email(email: str) -> Optional[Dict]:
    return users_coll.find_one({'email': email})


def update_user(user_id: str, update: Dict[str, Any]) -> Optional[Dict]:
    if not ObjectId.is_valid(user_id):
        return None
    users_coll.update_one({'_id': ObjectId(user_id)}, {'': update})
    return get_user_by_id(user_id)


def delete_user(user_id: str) -> bool:
    if not ObjectId.is_valid(user_id):
        return False
    res = users_coll.delete_one({'_id': ObjectId(user_id)})
    return res.deleted_count == 1


def list_users(filter: Dict[str, Any] = None) -> List[Dict]:
    if not filter:
        filter = {}
    return list(users_coll.find(filter))
