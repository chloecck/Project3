from typing import Tuple, Dict

from helper import (
    id_generator,
    generate_secret_key,
    ts_iso,
    check_str,
    check_id,
    check_username,
    purge_key_info,
)

""" Ext1
{
  id:int = id_generator()
  key:str = token_hex(16),
  timestamp:str = datetime.now().isoformat(),
  username:str, # Ext2
  user_bio:str # Ext2
}
"""
_users = {}
user_id_generator = id_generator()


def get_user_by_id(
    user_id: int, *, safe: bool = False
) -> Tuple[Dict, Tuple[Dict[str, str], int]]:
    user = {}
    user_id, err = check_id(user_id, "user_id")
    if err:
        return user, err

    user = _users.get(user_id)
    if user is None:
        return {}, ({"err": f"{user_id}: user not found"}, 404)

    if safe is True:
        user, err = purge_key_info(user)
        if err:
            return user, err

    return user, None


def get_user_by_username(
    username: str = None, *, safe: bool = False
) -> Tuple[Dict, Tuple[Dict[str, str], int]]:
    user = {}
    username, err = check_username(username)
    if err:
        return user, err

    for user in _users.values():
        if username == user.get("username"):
            if safe is True:
                user, err = purge_key_info(user)
                if err:
                    return user, err
            return user, None

    return {}, ({"err": f"{username}: user not found"}, 404)


def get_unique_metadata(
    *, user_id: int = None, username: str = None
) -> Tuple[Dict, Tuple[Dict[str, str], int]]:
    if user_id:
        user, err = get_user_by_id(user_id)
    elif username:
        user, err = get_user_by_username(username)
    else:
        return {}, (
            {"err": "'user_id' or username is required for user unique metadata"},
            400,
        )

    if err:
        return {}, err
    return {"user_id": user_id, "username": user.get("username")}, None


def get_non_unique_metadata(
    *, user_id: int = None, username: str = None
) -> Tuple[Dict, Tuple[Dict[str, str], int]]:
    if user_id:
        user, err = get_user_by_id(user_id)
    elif username:
        user, err = get_user_by_username(username)
    else:
        return {}, (
            {"err": "'user_id' or username is required for user non-unique metadata"},
            400,
        )

    if err:
        return {}, err
    return {"user_id": user_id, "user_bio": user.get("user_bio")}, None


def get_metadata(
    *, user_id: int = None, username: str = None
) -> Tuple[Dict, Tuple[Dict[str, str], int]]:
    if user_id:
        user_id, err = check_id(user_id, "user_id")
        if err:
            return {}, err
        non_unique_metadata, err = get_non_unique_metadata(user_id=user_id)
        if err:
            return {}, err
        unique_metadata, err = get_unique_metadata(user_id=user_id)
        if err:
            return {}, err
    elif username:
        username, err = check_username(username)
        if err:
            return {}, err
        non_unique_metadata, err = get_non_unique_metadata(username=username)
        if err:
            return {}, err
        unique_metadata, err = get_unique_metadata(username=username)
        if err:
            return {}, err
    else:
        return {}, ({"err": "'user_id' or username is required for user metadata"}, 400)

    return {**non_unique_metadata, **unique_metadata}, None


def update_metadata(
    user_id: int, user_key: str, username: str, user_bio: str
) -> Tuple[Dict, Tuple[Dict[str, str], int]]:
    user_id, err = check_id(user_id, "user_id")
    if err:
        return {}, err

    username, err = check_username(username)
    if err:
        return {}, err

    user_bio, err = check_str(user_bio, "user_bio")
    if err:
        return {}, err

    user, err = get_user_by_username(username)
    if user:
        return {}, ({"err": f"{username}: username already exists"}, 400)

    user, err = get_user_by_id(user_id)
    if err:
        return {}, err
    if user_key != user.get("user_key"):
        return {}, ({"err": f"{user_key}: did not match user {user_id}"}, 403)

    user.update({"username": username, "user_bio": user_bio})
    return {
        "user_id": user.get("user_id"),
        "username": user.get("username"),
        "user_bio": user.get("user_bio"),
    }, None


def create_user(
    username: str, user_bio: str = None
) -> Tuple[Dict, Tuple[Dict[str, str], int]]:
    username, err = check_username(username)
    if err:
        return {}, err

    if user_bio is not None:
        user_bio, err = check_str(user_bio, "user_bio")
        if err:
            return {}, err

    user, err = get_user_by_username(username)
    if user:
        return {}, ({"err": f"{username}: username already exists"}, 400)

    user_id = user_id_generator()
    user = {
        "user_id": user_id,
        "user_key": generate_secret_key(),
        "timestamp": ts_iso(),
        "username": username,
        "user_bio": user_bio,
    }

    _users[user_id] = user

    return user, None
