from typing import Optional, Literal, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from ...core.database import get_db

db = get_db()
user_communities = db.user_communities

# Ensure unique (uid, cid) index
try:
    user_communities.create_index([('uid', 1), ('cid', 1)], unique=True)
except Exception:
    pass


def join_community(uid: str, cid: str, role: str = 'member') -> Optional[Dict[str, Any]]:
    if not ObjectId.is_valid(uid) or not ObjectId.is_valid(cid):
        return None
    data = {'uid': uid, 'cid': cid, 'joined_at': datetime.now(), 'role': role}
    try:
        res = user_communities.insert_one(data)
        return user_communities.find_one({'_id': res.inserted_id})
    except Exception:
        # likely duplicate key or other db error
        return None


def leave_community(uid: str, cid: str) -> bool:
    if not ObjectId.is_valid(uid) or not ObjectId.is_valid(cid):
        return False
    res = user_communities.delete_one({'uid': uid, 'cid': cid})
    return res.deleted_count == 1


def is_member(uid: str, cid: str) -> bool:
    if not ObjectId.is_valid(uid) or not ObjectId.is_valid(cid):
        return False
    return user_communities.count_documents({'uid': uid, 'cid': cid}) > 0


def members_of_community(cid: str) -> List[Dict[str, Any]]:
    if not ObjectId.is_valid(cid):
        return []
    return list(user_communities.find({'cid': cid}))


def communities_for_user(uid: str) -> List[Dict[str, Any]]:
    if not ObjectId.is_valid(uid):
        return []
    return list(user_communities.find({'uid': uid}))
