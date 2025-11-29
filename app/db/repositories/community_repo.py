from typing import Dict, Any, Optional, List
from bson import ObjectId
from ...core.database import get_db

db = get_db()
communities_coll = db.communities


def create_community(data: Dict[str, Any]):
    res = communities_coll.insert_one(data)
    return communities_coll.find_one({'_id': res.inserted_id})


def get_community_by_id(cid: str) -> Optional[Dict[str, Any]]:
    if not ObjectId.is_valid(cid):
        return None
    return communities_coll.find_one({'_id': ObjectId(cid)})


def update_community(cid: str, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not ObjectId.is_valid(cid):
        return None
    communities_coll.update_one({'_id': ObjectId(cid)}, {'': update})
    return get_community_by_id(cid)


def delete_community(cid: str) -> bool:
    if not ObjectId.is_valid(cid):
        return False
    res = communities_coll.delete_one({'_id': ObjectId(cid)})
    return res.deleted_count == 1


def list_communities_for_owner(owner_uid: str) -> List[Dict[str, Any]]:
    return list(communities_coll.find({'owner': owner_uid}))
