from flask import Flask, request
import secrets
from datetime import datetime
import threading

lock = threading.Lock()

app = Flask(__name__)
# sample code from the prof
# from secrets import randbelow
# @app.get("/random/<int:sides>")
# def roll(sides):
#     if sides <= 0:
#         return {'err': 'need a positive number of sides'}, 400

#     return {'num': randbelow(sides) + 1}

# global data and helper function
posts = {}
users = {}
post_id_to_keys = {}  # for testing, should not really exist
user_id_to_keys = {}


def secret_key():
    return secrets.token_hex(16)


def create_user_helper(data):
    # data is checked before passed in
    with lock:
        # user fields: User creation must specify the unique part; it may specify the non-unique parts.
        user_id = len(users) + 1
        user_key = secret_key()
        user_name = data['username']
        real_name = data['real_name']
        user_profile = {
            'user_id': user_id,
            'user_key': user_key,
            'username': user_name,
            'real_name': real_name,  # not unique
            'user_unique_metadata': user_name,
            'user_non_unique_metadata': real_name
        }
        users[user_id] = user_profile
    return user_profile


def get_user_id_unique_nonunique(existed_user_id):
    user_profile = users.get(existed_user_id)
    return {
        'user_id': user_profile['user_id'],
        'user_unique_metadata': user_profile['username'],
        'user_non_unique_metadata': user_profile['real_name']
    }


# Endpoint 1: create a post with POST /post -> test in forum_multiple_posts.postman_collection.json and in forum_multiple_users.postman_collection.json
@app.route('/post', methods=['POST'])
def create_post():
    try:
        data = request.get_json()
        # If the input isn’t a JSON object or is missing the msg field or the msg isn’t a string, you should return status 400 (indicating ‘bad request’).        if not isinstance(data, dict) or 'msg' not in data or not isinstance(data['msg'], str):
        if not isinstance(data, dict) or 'msg' not in data or not isinstance(data['msg'], str):
            return {'err': "should be json object w msg field"}, 400
        # post fields
            # id should be an integer
            # key should be a long, unique random string (which is used to later delete the post)
            # timestamp should be an ISO 8601 timestamp in UTC
        with lock:
            post_id = len(posts) + 1
            post_key = secret_key()
            timestamp = datetime.utcnow().isoformat()
            new_post = {
                'id': post_id,
                'key': post_key,
                'timestamp': timestamp,
                'msg': data['msg'],
                # Extension 3: Threaded replies --> TODO: test (add to the end of the forum_multiple_posts.postman_collection.json file)
                # When creating a post, it should be possible to specify a post id to which the new post is replying.
                # When returning information about a post that is a reply, include the id of the post to which it is replying.
                # When returning information about a post which has replies, include the ids of every reply to that post
                'reply_to': data.get('reply_to', None),
                'has_reply': []
            }
            if new_post['reply_to']:
                mother_post = posts.get(new_post['reply_to'])
                mother_post['has_reply'].append(post_id)

            # Extension 1 Users and user keys: -> tested in in forum_multiple_users.postman_collection.json
            # Each post can be associated with a user by providing the user id and corresponding user key when creating the post.
            # Since user_id and user_key are non-editable, it can and will be passed into the posts database.
            user_id = data.get('user_id', None)
            # app.logger.error(
            #     'This is an error message of user_id.', {int(user_id)})
            user_key = data.get('user_key', None)
            # app.logger.error(
            #     'This is an error message of user_key.', {user_key})
            if (user_id and not user_key) or (user_key and not user_id):
                return {'err': 'if provide a user, it must contain both user_id and user_key'}, 400
            if user_id and user_key:
                user_profile = users.get(int(user_id), None)
                if not user_profile:
                    app.logger.error(
                        'This is an error message where user_profile cannot be found.', {user_profile})
                    return {'err': 'no user found with the user_id in the post POST method'}, 404
                if user_key != user_profile['user_key']:
                    return {'err': 'provided key does not match user\'s key'}, 404
            if user_id:
                new_post['user_id'] = int(user_id)
                new_post['user_key'] = str(user_key)
            # Add the post to the global data
            posts[post_id] = new_post

            # Return the response with post details and 200
            return_object = {
                'id': post_id,
                'timestamp': timestamp,
                'msg': data['msg'],
                'key': new_post['key'],
                # Extension 3: Threaded replies: --TODO: test: test (add to the end of the forum_multiple_posts.postman_collection.json file)
                # When returning information about a post that is a reply, include the id of the post to which it is replying.
                # When returning information about a post which has replies, include the ids of every reply to that post
                'reply_to': new_post['reply_to'],
                'has_reply': new_post['has_reply']
            }
            # Extension 1 Users and user keys:  -> tested in in forum_multiple_users.postman_collection.json
            # Whenever you give information about a post that has an associated user,
            # you should return the associated user id along with other data (e.g., when reading and deleting posts).
            # Extension 2 User Profile:  -> tested in in forum_multiple_users.postman_collection.json
            # When returning information about a post associated with a user, you must include the user’s unique metadata.
            # I also include user other data for the POST method return, and it should include the most updated user info (through retrieve the user database)
            if 'user_id' in new_post:
                return_object.update(
                    get_user_id_unique_nonunique(int(user_id)))
        return return_object, 200
    except Exception as e:
        return {'err': str(e)}, 404


# Endpoint2: read a post with GET /post/{{id}} -> test in forum_multiple_posts.postman_collection.json
@app.route('/post/<int:post_id>', methods=['GET'])
def read_post(post_id):
    try:
        with lock:
            post = posts.get(post_id, None)
            if not post:
                return {'err': 'No post found'}, 404
            # Return the response with post details (exclude key), and 200
            return_object = {
                'id': post['id'],
                'timestamp': post['timestamp'],
                'msg': post['msg'],
                'reply_to': post['reply_to'],
                'has_reply': post['has_reply']
            }
            # Extension 1 Users and user keys:  -> tested in in forum_multiple_users.postman_collection.json
            # Whenever you give information about a post that has an associated user,
            # you should return the associated user id along with other data (e.g., when reading and deleting posts).
            # Extension 2 User Profile:  -> tested in in forum_multiple_users.postman_collection.json
            # When returning information about a post associated with a user, you must include the user’s unique metadata.
            user_id = post.get('user_id', None)
            if user_id:
                return_object.update(get_user_id_unique_nonunique(user_id))
        return return_object, 200
    except Exception as e:
        return {'err': str(e)}, 404


# Endpoint 3: delete a post with DELETE /post/{{id}}/delete/{{key}} -> TODO: test (add to the end of the forum_multiple_users.postman_collection.json file)
@app.route('/post/<int:post_id>/delete/<string:key>', methods=['DELETE'])
def delete_post(post_id, key):
    try:
        with lock:
            post = posts.get(post_id, None)
            if not post:
                return {'err': 'No post found'}, 404
            if (key != post['key']):
                if ('user_key' in post and key != post['user_key']):
                    return {'err': 'provided key does not match post\'s key nor user\'s key'}, 403

            if post['reply_to']:
                mother_post = posts.get(post['reply_to'])
                mother_post['has_reply'].remove(post_id)
            # Delete the post
            del posts[post_id]
            # Return the response with post details (exclude key), and 200
            return_object = {
                'id': post['id'],
                'timestamp': post['timestamp'],
                'msg': post['msg'],
                # Extension 3: Threaded replies: --TODO: test (add to the end of the forum_multiple_posts.postman_collection.json file)
                # When returning information about a post that is a reply, include the id of the post to which it is replying.
                # When returning information about a post which has replies, include the ids of every reply to that post
                'reply_to': post['reply_to'],
                'has_reply': post['has_reply']
            }
            # Extension 1 Users and user keys:  -> tested in in forum_multiple_users.postman_collection.json
            # Whenever you give information about a post that has an associated user,
            # you should return the associated user id along with other data (e.g., when reading and deleting posts).
            # Extension 2 User Profile:  -> tested in in forum_multiple_users.postman_collection.json
            # When returning information about a post associated with a user, you must include the user’s unique metadata.
            user_id = post.get('user_id', None)
            if user_id:
                return_object.update(get_user_id_unique_nonunique(user_id))
        return return_object, 200
    except Exception as e:
        return {'err': str(e)}, 404


# Extension 1 and 2 User: create a user: -> test in forum_multiple_users.postman_collection.json
@app.route('/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not isinstance(data, dict) or ('username' not in data) or (not isinstance(data['username'], str)) or ('real_name' not in data) or (not isinstance(data['real_name'], str)):
            return {'err': "should be json object w username and real_name string field"}, 200
        user_profile = create_user_helper(data)
        # Return the response with user details with 200
        return user_profile, 200
    except Exception as e:
        return {'err': str(e)}, 404


# Extension2 User Profile: read a user: -> test in forum_multiple_users.postman_collection.json
@app.route('/user/<int:user_id>', methods=['GET'])
def read_user_metadata(user_id):
    try:
        with lock:
            user_profile = users.get(user_id, None)
            if not user_profile:
                return {'err': 'no user found'}, 404
        # Return the response with user details with 200
        return_obj = get_user_id_unique_nonunique(user_id)
        return return_obj, 200
    except Exception as e:
        return {'err': str(e)}, 404

# Extension2 User Profile: edit a user -> test in forum_multiple_users.postman_collection.json


@app.route('/user/<int:user_id>/edit/<string:user_key>', methods=['PUT'])
def edit_user_metadata(user_id, user_key):
    try:
        data = request.get_json()
        if not isinstance(data, dict) or 'username' not in data or not isinstance(data['username'], str) or 'real_name' not in data or not isinstance(data['real_name'], str):
            return {'err': "should be json object with both username and real_name string field"}, 400
        with lock:
            # Critical section where the global state (users) is accessed
            # Look up the user by id
            user_profile = users.get(user_id, None)
            if not user_profile:
                return {'err': 'No user found'}, 404
            if user_key != user_profile['user_key']:
                return {'err': 'provided user key does not match post\'s key'}, 403
            # Update user metadata
            user_profile['username'] = data.get(
                'username', user_profile['username'])
            user_profile['real_name'] = data.get(
                'real_name', user_profile['real_name'])
            # if there's no real update, treat as success update
        # Return the response with updated user details
        return_obj = get_user_id_unique_nonunique(user_id)
        return return_obj, 200
    except Exception as e:
        return {'err': str(e)}, 404


# TODO: the remaining two extension and write tests in a separete .json

if __name__ == '__main__':
    app.run(debug=True)
