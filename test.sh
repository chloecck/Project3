#!/bin/sh

set -e # exit immediately if newman complains
trap 'kill $PID' EXIT # kill the server on exit

./run.sh &
PID=$! # record the PID

<<<<<<< HEAD
newman run post_read_delete.postman_collection.json 5 # 5 iterations
newman run multiple_posts.postman_collection.json -e env.json # use the env file
newman run posts_and_users.postman_collection.json -e env.json # use the env file
newman run users.postman_collection.json -e env.json # use the env file

=======
newman run "s01.forum- post" 5 # 50 iterations
newman run forum_multiple_posts.postman_collection.json -e env.json # use the env file
newman run forum_multiple_users.postman_collection.json -e env.json # use the env file
>>>>>>> 49b9309d7f44f374fab7dd7acef54976d891cc95


