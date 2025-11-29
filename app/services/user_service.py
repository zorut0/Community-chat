from ...db.repositories import user_repo
from typing import Dict, Any, Optional


def create_user(payload: Dict[str, Any]) -> Dict[str, Any]:
    # check email uniqueness
    existing = user_repo.get_user_by_email(payload.get('email'))
    if existing:
        raise ValueError('email already exists')
    return user_repo.create_user(payload)


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    return user_repo.get_user_by_id(user_id)


def update_user(user_id: str, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return user_repo.update_user(user_id, update)


def delete_user(user_id: str) -> bool:
    return user_repo.delete_user(user_id)


def list_users() -> list:
    return user_repo.list_users()
