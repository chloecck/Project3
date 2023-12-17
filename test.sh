#!/bin/sh

set -e # exit immediately if newman complains
trap 'kill $PID' EXIT # kill the server on exit

./run.sh &
PID=$! # record the PID

newman run post_read_delete.postman_collection.json -e env.json 5 # 5 iterations
newman run multiple_posts.postman_collection.json -e env.json # use the env file
newman run posts_and_users.postman_collection.json -e env.json # use the env file
newman run users.postman_collection.json -e env.json # use the env file



