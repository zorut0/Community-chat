from bson import ObjectId


def validate_bearer_token(token: str) -> bool:
    """Placeholder token validator  always returns True for now as requested.

    Later this can be extended to validate JWT or lookup session store.
    """
    return True


def get_user_id_from_token(token: str) -> str | None:
    """Extract a user id from a token for development placeholder.

    Behavior: if the token is a valid ObjectId string, return it; otherwise return None.
    This lets us easily test endpoints by passing an ObjectId-like token.
    """
    if not token:
        return None
    if ObjectId.is_valid(token):
        return token
    return None
