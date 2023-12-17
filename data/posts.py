from datetime import datetime
from typing import Dict, List, Tuple

from data import users
from helper import (
    check_id,
    check_str,
    check_ts_iso,
    check_username,
    generate_secret_key,
    id_generator,
    purge_key_info,
    ts_iso,
    dicts_intersection,
)

"""
{
  post_id:int = id_generator(),
  post_key:str = token_hex(16),
  timestamp:str = datetime.utcnow().isoformat(),
  msg:str,
  user_id:int = uuid4().int, # Ext1
  user_key:str = token_hex(16), # Ext1
  username:str, # Ext2
  user_bio:str, # Ext2
  reply_to:post_id, # Ext3
  replies:List[post_id] #Ext3
}
"""
_posts = {}
post_id_generator = id_generator()


def create_post(
    msg: str,
    *,
    user_id: int = None,
    user_key: str = None,
    reply_to: int = None,
) -> Tuple[Dict, Tuple[Dict, int]]:
    msg, err = check_str(msg, "msg")
    if err:
        return {}, err

    post_id = post_id_generator()
    post = {
        "post_id": post_id,
        "post_key": generate_secret_key(),
        "timestamp": ts_iso(),
        "msg": msg,
        "replies": [],
    }

    if (user_id is None) ^ (user_key is None):
        return post, (
            {"err": "'user_id' and 'user_key' should be provided together"},
            400,
        )

    if user_id is not None:
        user, err = users.get_user_by_id(user_id)
        if err:
            return post, err
        if user.get("user_key") != user_key:
            return post, ({"err": f"{user_key}: did not match user{user_id}"}, 403)
        user_unique_metadata, err = users.get_unique_metadata(user_id=user_id)
        if err:
            return post, err

        post.update({"user_id": user_id, "user_key": user_key, **user_unique_metadata})

    if reply_to is not None:
        replied, err = get_post_by_id(reply_to)
        if err:
            return post, err
        post.update({"reply_to": reply_to})
        replied.get("replies").append(post_id)

    _posts[post_id] = post
    return post, None


def get_post_by_id(
    post_id: int, *, safe: bool = False
) -> Tuple[Dict, Tuple[Dict, int]]:
    post = {}
    post_id, err = check_id(post_id, "post_id")
    if err:
        return post, err

    post = _posts.get(post_id)
    if post is None:
        return post, ({"err": f"{post_id}: post not found"}, 404)

    if safe is True:
        post, err = purge_key_info(post)
        if err:
            return post, err
    return post, None


def delete_post(
    post_id: int, key: str = None, /, *, is_user_key: bool = None, safe: bool = False
) -> Tuple[Dict, Tuple[Dict, int]]:
    post_id, err = check_id(post_id, "post_id")
    post, err = get_post_by_id(post_id)
    if err:
        return None, err

    if post_id not in _posts:
        return None, ({"err": f"{post_id}: post not found"}, 404)

    if is_user_key is not None:
        if not isinstance(is_user_key, bool):
            return None, (
                {"err": f"{is_user_key}: 'is_user_key' should be a boolean"},
                400,
            )

    if is_user_key:
        if post.get("user_key") != key:
            return None, ({"err": f"{key}: did not match post {post_id} user_key"}, 403)
    else:
        if post.get("post_key") != key:
            return None, ({"err": f"{key}: did not match post {post_id} post_key"}, 403)

    del _posts[post_id]

    if safe is True:
        post, err = purge_key_info(post)
        if err:
            return post, err
    return post, None


def get_posts_by_time_range(
    start: str = None, end: str = None, *, safe: bool = False
) -> Tuple[List[Dict], Tuple[Dict, int]]:
    if start is None and end is None:
        return [], (
            {"err": f"({start}, {end}): start or/and end is required for the query"},
            400,
        )

    if start is not None:
        start, err = check_ts_iso(start, "start timestamp")
        if err:
            return [], err

    if end is not None:
        end, err = check_ts_iso(end, "end timestamp")
        if err:
            return [], err

    if start is not None and end is not None:
        if start >= end:
            return [], ({"err": f"start {start} after end {end}"}, 400)

    res = []
    for post in _posts:
        ts = datetime.fromisoformat(post.get("timestamp"))
        if ((start is None or ts >= start)) and (end is None or ts <= end):
            if safe is True:
                post, err = purge_key_info(post)
                if err:
                    return res, err
            res.append(post)

    return res, None


def get_posts_by_user(
    user_id: int, username: str, *, safe: bool = False
) -> Tuple[List[Dict], Tuple[Dict, int]]:
    if user_id is None and username is None:
        return [], (
            {
                "err": f"({user_id}, {username}): 'user_id' or/and 'username' is required for the query"
            },
            400,
        )

    if user_id is not None:
        user_id, err = check_id(user_id, "user_id")
        if err:
            return [], err

    if username is not None:
        username, err = check_username(username, "end timestamp")
        if err:
            return [], err

    res = []
    for post in _posts:
        if ((user_id is None or user_id == post.get("user_id"))) and (
            username is None or username == post.get("username")
        ):
            if safe is True:
                post, err = purge_key_info(post)
                if err:
                    return res, err
            res.append(post)

    return res, None


def get_posts_by_queries(
    *,
    start: str = None,
    end: str = None,
    user_id: int = None,
    username: str = None,
    safe: bool = False,
) -> Tuple[List[Dict], Tuple[Dict, int]]:
    if start is None and end is None and user_id is None and username is None:
        return [], (
            {"err": "'start', 'end', 'user_id' or 'username' is required for query"},
            400,
        )

    posts_by_time = []
    if start or end:
        posts_by_time, err = get_posts_by_time_range(start, end, safe=safe)
        if err:
            return [], err

    posts_by_user = []
    if user_id or username:
        posts_by_user, err = get_posts_by_user(user_id, username, safe=safe)
        if err:
            return [], err

    post, err = dicts_intersection(posts_by_time, posts_by_user)
    if err:
        return [], err

    return post, None
