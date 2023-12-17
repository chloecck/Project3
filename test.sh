#!/bin/sh

set -e # exit immediately if newman complains
trap 'kill $PID' EXIT # kill the server on exit

./run.sh &
PID=$! # record the PID

newman run "s01.forum- post" 5 # 50 iterations
newman run forum_multiple_posts.postman_collection.json -e env.json # use the env file
newman run forum_multiple_users.postman_collection.json -e env.json # use the env file


