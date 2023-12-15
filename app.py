from datetime import datetime
from threading import RLock
from typing import Dict

from flask import Flask, request

from config import register_errorhandlers
from helper import check_username, extract_from_json, generate_secret_key, id_generator

lock = RLock()
app = Flask(__name__)
register_errorhandlers(app, request)


"""
{
  id:int = id_generator(), # int starting from 1
  key:str = token_hex(16),
  timestamp:str = datetime.now().isoformat(),
  user_id:int = id_generator, # Ext1
  user_key:str = token_hex(16), # Ext1
  **user_unique_metadata, # Ext2
  reply_to, # Ext3
  replies:list = , # Ext3
}
"""
posts = {}
""" Ext1
{
  id:int = id_generator()
  key:str = token_hex(16),
  timestamp:str = datetime.now().isoformat(),
  username:str, # Ext2
  display_name:str # Ext2
}
"""
users = {}

post_id_generator = id_generator()
user_id_generator = id_generator()


def get_user_unique_metadata(
    users: Dict[str, Dict], user_id_target: int = None, username_target: str = None
) -> dict:
    if user_id_target is not None:
        assert user_id_target in users, f"{user_id_target}: user not found"
        user = users.get(user_id_target)
        return {"user_id": user_id_target, "username": user.get("username")}

    if username_target is not None:
        for user_id_target, user in users.items():
            if user.get("username") == username_target:
                return {"user_id": user_id_target, "username": username_target}

    return None


def get_user_non_unique_metadata(
    users: Dict[str, Dict], user_id_target: int = None, username_target: str = None
) -> dict:
    if user_id_target is not None:
        assert user_id_target in users, f"{user_id_target}: user not found"
        user = users.get(user_id_target)
        return {"user_id": user_id_target, "display_name": user.get("display_name")}

    if username_target is not None:
        for user_id_target, user in users.items():
            if user.get("username") == username_target:
                return {
                    "user_id": user_id_target,
                    "display_name": user.get("display_name"),
                }

    return None


def get_user_metadata(
    users: Dict[str, Dict], user_id_target: int = None, username_target: str = None
) -> dict:
    user_non_unique_metadata = get_user_non_unique_metadata(
        users, user_id_target, username_target
    )
    user_unique_metadata = get_user_non_unique_metadata(
        users, user_id_target, username_target
    )

    if user_non_unique_metadata and user_unique_metadata:
        return {
            **get_user_non_unique_metadata(users, user_id_target),
            **get_user_unique_metadata(users, user_id_target),
        }

    if user_non_unique_metadata:
        return user_non_unique_metadata

    if user_unique_metadata:
        return user_unique_metadata

    return None


def get_post(posts: Dict[str, Dict], users: Dict[str, Dict], post_id: int) -> dict:
    post = posts.get(post_id)
    user_id = post.get("user_id")  # Ext 1
    user_unique_metadata = get_user_unique_metadata(users, user_id) or {}
    reply_to = post.get("reply_to")  # Ext3
    replies = post.get("replies")  # Ext3

    res = {
        "id": post.get("id"),
        "timestamp": post.get("timestamp"),
        "msg": post.get("msg"),
        "user_id": post.get("user_id"),  # Ext1:
        # Whenever you give information about a post that has an associated user, you should return the associated user id along with other data (e.g., when reading and deleting posts).
        **user_unique_metadata,  # Ext2:
        # When returning information about a post associated with a user, you must include the user’s unique metadata.
    }

    # Ext3:
    # When returning information about a post that is a reply, include the id of the post to which it is replying.
    # When returning information about a post which has replies, include the ids of every reply to that post.
    if reply_to:
        res.update({"reply_to": reply_to})
    if replies:
        res.update({"replies": replies})

    return res


@app.post("/post")
def create_post():
    data: dict = request.get_json()
    msg = extract_from_json(data, "msg", vtype=str)

    # Ext1: Users and user Keys
    # Each post can be associated with a user by providing the user id and corresponding user key when creating the post.
    user_id = data.get("user_id")  # Ext1
    user_key = data.get("user_key")  # Ext1
    assert not (
        (user_id is None) ^ (user_key is None)
    ), '"user_id" and "user_key" should be provided together'

    with lock:
        if user_id:
            if user_id not in users:
                return {"err": f"{user_id}: user not found"}, 404
            user: dict = users.get(user_id)

            user_key_to_compare = user.get("key")
            if user_key != user_key_to_compare:
                return {"err": f"{user_key}: did not match user {user_id}"}, 403

        id = post_id_generator()
        key = generate_secret_key()
        timestamp = datetime.now().isoformat()

        user_unique_metadata = get_user_unique_metadata(users, user_id) or {}  # Ext2

        reply_to = data.get("reply_to")  # Ext3
        if reply_to:
            if reply_to not in posts:
                return {"err": f"{reply_to}: not found in posts"}, 404
            replied_post = posts.get(reply_to)
            replied_post.get("replies").append(id)

        posts[id] = {
            "id": id,
            "key": key,
            "timestamp": timestamp,
            "msg": msg,
            "user_id": user_id,  # Ext1
            "user_key": user_key,  # Ext1
            **user_unique_metadata,  # Ext2
            "reply_to": reply_to,  # Ext3:
            # When creating a post, it should be possible to specify a post id to which the new post is replying.
            "replies": [],  # Ext3
        }

        res = {
            "id": id,
            "key": key,
            "timestamp": timestamp,
            "user_id": user_id,  # Ext1:
            # Whenever you give information about a post that has an associated user, you should return the associated user id along with other data (e.g., when reading and deleting posts).
            **user_unique_metadata,  # Ext2:
            # When returning information about a post associated with a user, you must include the user’s unique metadata.
        }

        # Ext3:
        # When returning information about a post that is a reply, include the id of the post to which it is replying.
        if reply_to:
            res.update({"reply_to": reply_to})

        return res


@app.get("/post/<int:id>")
def read_post(id: int):
    with lock:
        if id not in posts:
            return {"err": "Post not found"}, 404

        post: dict = posts[id]
        user_id = post.get("user_id")  # Ext1
        user_unique_metadata = get_user_unique_metadata(users, user_id) or {}  # Ext2
        reply_to = post.get("reply_to")  # Ext3
        replies = post.get("replies")  # Ext3

        res = {
            "id": post.get("id"),
            "timestamp": post.get("timestamp"),
            "msg": post.get("msg"),
            "user_id": user_id,  # Ext1:
            # Whenever you give information about a post that has an associated user, you should return the associated user id along with other data (e.g., when reading and deleting posts).
            **user_unique_metadata,  # Ext2:
            # When returning information about a post associated with a user, you must include the user’s unique metadata.
        }

        # Ext3:
        # When returning information about a post that is a reply, include the id of the post to which it is replying.
        # When returning information about a post which has replies, include the ids of every reply to that post.
        if reply_to:
            res.update({"reply_to": reply_to})
        if replies:
            res.update({"replies": replies})

        return res


@app.delete("/post/<int:id>/delete/<string:key>")
def delete_post(id: int, key: str):
    with lock:
        if id not in posts:
            return {"err": "Post not found"}, 404

        post: dict = posts.get(id)
        key_to_compare = post.get("key")

        # Ext1:
        # If a user created a post, it should be sufficient to provide the user’s key to delete the post. It should be clear whether the user is providing a post’s key or a user’s key.
        if request.is_json and (data := request.get_json()):
            if isinstance(data, dict) and data.get("is_user_key"):
                key_to_compare = post.get("user_key")

        if key != key_to_compare:
            return {"err": "Keys do not match"}, 403

        del posts[id]

        user_id = post.get("user_id")  # Ext1
        user_unique_metadata = get_user_unique_metadata(users, user_id) or {}  # Ext2
        reply_to = post.get("reply_to")  # Ext3
        replies = post.get("replies")  # Ext3

        res = {
            "id": id,
            "key": key,
            "timestamp": post.get("timestamp"),
            "user_id": user_id,  # Ext1
            # Whenever you give information about a post that has an associated user, you should return the associated user id along with other data (e.g., when reading and deleting posts).
            **user_unique_metadata,  # Ext2
            # When returning information about a post associated with a user, you must include the user’s unique metadata.
        }

        # Ext3:
        # When returning information about a post that is a reply, include the id of the post to which it is replying.
        # When returning information about a post which has replies, include the ids of every reply to that post.
        if reply_to:
            res.update({"reply_to": reply_to})
        if replies:
            res.update({"replies": replies})

        return res


# Ext1: There should be some way to create users.
@app.post("/user")
def create_user():
    data = request.get_json()

    # Ext2: User profiles
    # User creation must specify the unique part; it may specify the non-unique parts.
    username = extract_from_json(data, "username", vtype=str)
    username = check_username(username)
    display_name = data.get("display_name")
    if display_name:
        assert isinstance(display_name, str), '"display_name" was not a string'

    id = user_id_generator()
    key = generate_secret_key()
    timestamp = datetime.now().isoformat()

    with lock:
        user = {
            "id": id,
            "key": key,
            "timestamp": timestamp,
            "username": username,
            "display_name": display_name,
        }

        users[id] = user

    return user


# Ext2: retrieve a given user’s metadata given their id or their unique metadata
@app.get("/user")
def read_user_metadata():
    username = request.args.get("username", "")
    id = request.args.get("id", type=int)

    assert (
        username is not None or id is not None
    ), '"username" or "id" is required for metadata'
    if username:
        username = check_username(username)

    with lock:
        for user_id, user in users.items():
            if user_id == id:
                return get_user_metadata(users, user_id)
            if user.get("username") == username:
                return get_user_metadata(users, user_id)

        return {"err": "user not found"}, 404


# Ext2: edit a given user’s metadata; doing so requires the user’s key.
@app.put("/user/<int:id>/edit/<string:key>")
def edit_user_metadata(id: int, key: str):
    data = request.get_json()
    username = extract_from_json(data, "username", vtype=str)
    display_name = extract_from_json(data, "display_name", vtype=str)

    username = check_username(username)

    with lock:
        if id not in users:
            return {"err": f"{id}: user not found"}, 404

        the_user: dict = users.get(id)
        if key != the_user.get("key"):
            return {"err": f"{key}: did not match user {id}"}, 403

        for user_id, user in users.items():
            if user.get("username") == username:
                return {"err": f"{username}: already exists"}, 400

        the_user.update({"username": username, "display_name": display_name})
        return {"user_id": id, "username": username, "display_name": display_name}


# Ext4: Date- and time-based range queries
# Ext5: User-based range queries
@app.get("/post")
def read_posts_queries():
    start = request.args.get("start", type=datetime.fromisoformat)  # Ext4
    end = request.args.get("end", type=datetime.fromisoformat)  # Ext4
    user_id_target = request.args.get("user_id", type=int)  # Ext5
    username_target = request.args.get("username", type=str)  # Ext5

    res = []
    with lock:
        for post in posts.values():
            timestamp = datetime.fromisoformat(post.get("timestamp"))
            user_id = post.get("user_id")  # Ext1
            username = post.get("username")  # Ext2
            if (
                (start is None or timestamp >= start)  # Ext4
                and (end is None or timestamp <= end)  # Ext4
                and (user_id_target is None or user_id_target == user_id)  # Ext5
                and (username_target is None or username_target == username)  # Ext5
            ):
                user_unique_metadata = (
                    get_user_unique_metadata(users, user_id, username) or {}
                )  # Ext2
                reply_to = post.get("reply_to")  # Ext3
                replies = post.get("replies")  # Ext3

                post_in_range = {
                    "id": post.get("id"),
                    "timestamp": post.get("timestamp"),
                    "msg": post.get("msg"),
                    "user_id": user_id,  # Ext1:
                    # Whenever you give information about a post that has an associated user, you should return the associated user id along with other data (e.g., when reading and deleting posts).
                    **user_unique_metadata,  # Ext2:
                    # When returning information about a post associated with a user, you must include the user’s unique metadata.
                }

                # Ext3:
                # When returning information about a post that is a reply, include the id of the post to which it is replying.
                # When returning information about a post which has replies, include the ids of every reply to that post.
                if reply_to:
                    post_in_range.update({"reply_to": reply_to})
                if replies:
                    post_in_range.update({"replies": replies})

                res.append(post_in_range)

    return res


if __name__ == "__main__":
    app.run(debug=True)
