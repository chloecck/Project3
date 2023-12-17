#!/bin/sh

set -e # exit immediately if newman complains
trap 'kill $PID' EXIT # kill the server on exit

./run.sh &
PID=$! # record the PID

# python -m unittest discover -s tests

# # newman run try.postman_collection.json
# newman run s01+forum-multiple_posts.postman_collection.json -e env.json
# newman run s02+forum-post_read_delete.postman_collection.json -e env.json
# newman run s03+forum-users.postman_collection.json -e env.json
newman run s04+forum-posts_users.postman_collection.json