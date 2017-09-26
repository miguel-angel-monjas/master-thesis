# Saving data to Elasticsearch indices
The [Elastic Stack](https://www.elastic.co/products) (formerly the ELK Stack) is a set of open source tools to search, analyze and visualize data in real time. Although the combination of Jupyter notebooks with `matplotlib` provides a compelling way of showing results, there are situations in which a more powerful tool is required. Thus, the following guidelines will describe how to set up and configure a Elastic Stack instance and how to make it accessible from a Spark Standalone cluster.

----
## Pre-requisites
Docker and Docker Compose will be used to deploy an Elastic Stack in an Openstack instance. Thus, Docker CE and Docker Compose have to be installed. The following script will be used (taken from the official Docker documentation on [Docker CE](https://docs.docker.com/engine/installation/linux/ubuntu/) and [Docker Compose](https://docs.docker.com/compose/install/)):

```bash
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

# Docker group management (https://docs.docker.com/engine/installation/linux/linux-postinstall/)
sudo groupadd docker
sudo usermod -aG docker ubuntu
```

## Elasticsearch index definition

## Spark configuration