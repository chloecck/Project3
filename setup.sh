#!/bin/sh

# uncomment the line below to install some-package
# pip3 install flask

npm cache clean -f
npm install -g n
n stable

npm install newman
pip install faker
