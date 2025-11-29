from typing import Dict, Any, Optional, List
from datetime import datetime

from ...db.repositories import community_repo, user_repo, user_community_repo, message_repo


def create_community(payload: Dict[str, Any]) -> Dict[str, Any]:
    # owner must exist
    owner = user_repo.get_user_by_id(payload.get('owner'))
    if not owner:
        raise ValueError('owner user does not exist')

    community = community_repo.create_community(payload)

    # automatically add owner as member with owner role
    user_community_repo.join_community(payload.get('owner'), str(community.get('_id') if community else ''), role='owner')
    return community


def get_community(cid: str) -> Optional[Dict[str, Any]]:
    return community_repo.get_community_by_id(cid)


def update_community(cid: str, requesting_uid: str, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    community = community_repo.get_community_by_id(cid)
    if not community:
        return None
    if community.get('owner') != requesting_uid:
        raise PermissionError('only owner can update community')
    # only allow name and description changes
    allowed = {k: v for k, v in update.items() if k in ('name', 'description')}
    if not allowed:
        return community
    allowed['updated_at'] = datetime.now()
    return community_repo.update_community(cid, allowed)


def delete_community(cid: str, requesting_uid: str) -> bool:
    community = community_repo.get_community_by_id(cid)
    if not community:
        return False
    if community.get('owner') != requesting_uid:
        raise PermissionError('only owner can delete community')
    # delete community, memberships, and messages
    community_deleted = community_repo.delete_community(cid)
    if community_deleted:
        # remove memberships
        _ = user_community_repo.members_of_community(cid)
        # delete all memberships
        from ...core.database import get_db
        db = get_db()
        db.user_communities.delete_many({'cid': cid})
        # delete messages
        db.messages.delete_many({'cid': cid})
    return community_deleted


def list_communities_for_owner(owner_uid: str) -> List[Dict[str, Any]]:
    return community_repo.list_communities_for_owner(owner_uid)
