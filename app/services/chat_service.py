from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId

from ...db.repositories import (
    message_repo,
    user_repo,
    community_repo,
    user_community_repo,
)

# spam / rate limit configuration
MAX_MESSAGES_PER_MINUTE = 5


def _validate_ids(uid: str, cid: str) -> bool:
    return ObjectId.is_valid(uid) and ObjectId.is_valid(cid)


def send_message(uid: str, cid: str, text: str) -> Dict[str, Any]:
    # basic id validation
    if not _validate_ids(uid, cid):
        raise ValueError('uid and cid must be valid ObjectId strings')

    # user and community must exist
    user = user_repo.get_user_by_id(uid)
    if not user:
        raise ValueError('user does not exist')
    community = community_repo.get_community_by_id(cid)
    if not community:
        raise ValueError('community does not exist')

    # ensure user belongs to community
    if not user_community_repo.is_member(uid, cid):
        raise ValueError('user is not a member of this community')

    # spam prevention: count recent messages by same user in this community
    recent_count = message_repo.count_recent_messages_by_user(uid, cid, seconds=60)
    if recent_count >= MAX_MESSAGES_PER_MINUTE:
        raise ValueError('rate limit exceeded')

    # create message
    payload = {'uid': uid, 'cid': cid, 'text': text, 'created_at': datetime.now()}
    return message_repo.create_message(payload)


def update_message(mid: str, requesting_uid: str, new_text: str) -> Optional[Dict[str, Any]]:
    if not ObjectId.is_valid(mid):
        raise ValueError('message id must be a valid ObjectId')

    message = message_repo.get_message_by_id(mid)
    if not message:
        return None

    # determine whether requesting user is allowed (message owner or community owner)
    is_author = message.get('uid') == requesting_uid
    community = community_repo.get_community_by_id(message.get('cid'))
    is_community_owner = community and community.get('owner') == requesting_uid

    if not (is_author or is_community_owner):
        raise PermissionError('not authorized to update this message')

    # apply update (only text allowed)
    return message_repo.update_message(mid, {'text': new_text})


def delete_message(mid: str, requesting_uid: str) -> bool:
    if not ObjectId.is_valid(mid):
        raise ValueError('message id must be a valid ObjectId')

    message = message_repo.get_message_by_id(mid)
    if not message:
        return False

    is_author = message.get('uid') == requesting_uid
    community = community_repo.get_community_by_id(message.get('cid'))
    is_community_owner = community and community.get('owner') == requesting_uid

    if not (is_author or is_community_owner):
        raise PermissionError('not authorized to delete this message')

    return message_repo.delete_message(mid)


def list_messages(cid: str, limit: int = 100) -> List[Dict[str, Any]]:
    return message_repo.list_messages_by_community(cid, limit=limit)
