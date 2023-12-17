from threading import Lock

from flask import Flask, request
from werkzeug.exceptions import UnsupportedMediaType


from config import config_app
from data import posts, users
from helper import extract_from_json

lock = Lock()
app = Flask(__name__)
config_app(app, request)


@app.post("/post")
def create_post():
    data: dict = request.get_json()

    msg = extract_from_json(data, "msg", vtype=str)
    assert msg, "'msg' was empty"

    user_id = extract_from_json(data, "user_id", required=False)
    user_key = extract_from_json(data, "user_key", required=False)
    reply_to = extract_from_json(data, "reply_to", required=False)

    with lock:
        post, err = posts.create_post(
            msg, user_id=user_id, user_key=user_key, reply_to=reply_to
        )
        if err:
            return err

        res = post.copy()
        res.update({"id": res.get("post_id"), "key": res.get("post_key")})
        res.pop("post_id")
        res.pop("post_key")
        return res


@app.get("/post/<int:post_id>")
def read_post(post_id: int):
    with lock:
        post, err = posts.get_post_by_id(post_id, safe=True)
        if err:
            return err

        res = post.copy()
        res.update({"id": res.get("post_id")})
        res.pop("post_id")
        return res


@app.delete("/post/<int:post_id>/delete/<string:key>")
def delete_post(post_id: int, key: str):
    try:
        data: dict = request.get_json()
    except UnsupportedMediaType:
        data = {}

    is_user_key = data.get("is_user_key")
    if is_user_key is not None:
        assert isinstance(is_user_key, bool), "is_user_key should be a boolean"

    with lock:
        post, err = posts.delete_post(post_id, key, is_user_key=is_user_key, safe=True)
        if err:
            return err

        res = post.copy()
        res.update({"id": res.get("post_id")})
        res.pop("post_id")
        return res


@app.post("/user")
def create_user():
    data = request.get_json()

    username = extract_from_json(data, "username", vtype=str)
    user_bio = extract_from_json(data, "user_bio", vtype=str, required=False)

    with lock:
        user, err = users.create_user(username, user_bio)
        if err:
            return err

        res = user.copy()
        res.update({"id": res.get("user_id"), "key": res.get("user_key")})
        res.pop("user_id")
        res.pop("user_key")
        return res


@app.get("/user")
def read_user_metadata():
    user_id = request.args.get("user_id", type=int)
    username = request.args.get("username", type=str)
    assert (
        user_id is not None or username is not None
    ), "'user_id' or 'id' is required for metadata"

    with lock:
        user_metadata, err = users.get_metadata(user_id=user_id, username=username)
        if err:
            return err

        res = user_metadata.copy()
        res.update({"id": res.get("user_id")})
        res.pop("user_id")
        return res


@app.put("/user/<int:user_id>/edit/<string:user_key>")
def edit_user_metadata(user_id: int, user_key: str):
    data = request.get_json()

    username = extract_from_json(data, "username", vtype=str, required=True)
    user_bio = extract_from_json(data, "user_bio", vtype=str, required=True)

    with lock:
        metadata, err = users.update_metadata(user_id, user_key, username, user_bio)
        if err:
            return err

        res = metadata.copy()
        res.update({"id": res.get("user_id")})
        res.pop("user_id")
        return res


@app.get("/post")
def read_posts_queries():
    start = request.args.get("start")
    end = request.args.get("end")
    user_id = request.args.get("user_id", type=int)
    username = request.args.get("username", type=str)

    assert (
        start is not None or end is not None or user_id is not None or username is None
    ), "'start', 'end', 'user_id' or 'username' is required for query"

    with lock:
        posts_queried, err = posts.get_posts_by_queries(
            start=start, end=end, user_id=user_id, username=username, safe=True
        )
        if err:
            return err

        res = posts_queried.copy()
        for post in posts_queried:
            post.update({"id": post.get("post_id"), "key": post.get("post_key")})
            post.pop("post_id")
            post.pop("post_key")
        return res


if __name__ == "__main__":
    app.run(debug=True)
