#!/bin/sh

set -e # exit immediately if newman complains
trap 'kill $PID' EXIT # kill the server on exit

./run.sh &
PID=$! # record the PID

newman run s01+forum-multiple_posts.postman_collection -e env.json
newman run s02+forum-post_read_delete.postman_collection -e env.jsom
newman run s03+forum-users.postman_collection -e env.json
newman run s04+forum-posts_users.postman_collection -e env.json
