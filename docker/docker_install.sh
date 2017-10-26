#!/bin/sh

# Docker installation
echo "installing Docker CE"
sudo apt-get update -y
sudo apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual -y
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt-get update -y
sudo apt-get install docker-ce -y

# Docker Compose Installation
echo "installing Docker Compose"
sudo apt-get install software-properties-common -y
sudo apt-add-repository universe -y
sudo apt-get update -y
sudo apt-get install python-pip -y
sudo pip install --upgrade pip
sudo pip install docker-compose