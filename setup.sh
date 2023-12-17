#!/bin/sh

# uncomment the line below to install some-package
# pip3 install flask

sudo npm cache clean -f
sudo npm install -g n
sudo n stable

npm install newman
pip install faker
