from typing import Dict, Any, Optional, List
from bson import ObjectId
from ...core.database import get_db

db = get_db()
messages_coll = db.messages


def create_message(data: Dict[str, Any]) -> Dict[str, Any]:
    res = messages_coll.insert_one(data)
    return messages_coll.find_one({'_id': res.inserted_id})


def get_message_by_id(mid: str) -> Optional[Dict[str, Any]]:
    if not ObjectId.is_valid(mid):
        return None
    return messages_coll.find_one({'_id': ObjectId(mid)})


def update_message(mid: str, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not ObjectId.is_valid(mid):
        return None
    messages_coll.update_one({'_id': ObjectId(mid)}, {'': update})
    return get_message_by_id(mid)


def delete_message(mid: str) -> bool:
    if not ObjectId.is_valid(mid):
        return False
    res = messages_coll.delete_one({'_id': ObjectId(mid)})
    return res.deleted_count == 1


def list_messages_by_community(cid: str, limit: int = 100) -> List[Dict[str, Any]]:
    if not ObjectId.is_valid(cid):
        return []
    return list(messages_coll.find({'cid': cid}).sort('created_at', -1).limit(limit))


def count_recent_messages_by_user(uid: str, cid: str, seconds: int = 60) -> int:
    from datetime import datetime, timedelta
    if not ObjectId.is_valid(uid):
        return 0
    since = datetime.now() - timedelta(seconds=seconds)
    return messages_coll.count_documents({'uid': uid, 'cid': cid, 'created_at': {'': since}})
