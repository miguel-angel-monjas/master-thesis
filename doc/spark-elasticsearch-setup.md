# Saving data to Elasticsearch indices
The [Elastic Stack](https://www.elastic.co/products) (formerly the ELK Stack) is a set of open source tools to search, analyze and visualize data in real time. Although the combination of Jupyter notebooks with `matplotlib` provides a compelling way of showing results, there are situations in which a more powerful tool is required. Thus, the following guidelines will describe how to set up and configure a Elastic Stack instance and how to make it accessible from a Spark Standalone cluster.

----
## Pre-requisites
The deployment of Elastic Stack on an Openstack instance will be carried out by means of Docker containers. Thus, Docker CE and Docker Compose have to be installed before the containers can be created. It can be done by executing a shell script with the following content (taken from the official Docker documentation on [Docker CE](https://docs.docker.com/engine/installation/linux/ubuntu/) and [Docker Compose](https://docs.docker.com/compose/install/)):

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
```

The shell script, `docker_install.sh` is availabe in the `elastic` folder in the Github repo. 

The instance name must be registered in the instances of the HDFS cluster (in the Elastic Stack instance as well) by executing the following command:

```bash
echo "
<elk-ip-address>		elk
" | sudo tee --append /etc/hosts
```

Next, we execute the following commands in order to enable docker use without `sudo` privileges (from [here] (https://docs.docker.com/engine/installation/linux/linux-postinstall/)):
```bash
sudo groupadd docker
sudo usermod -aG docker ubuntu
```

Finally, a limit on mmap counts equal to 262,144 or more has to be set. It can be done by executing the following command (see the [official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html)):

```bash
sudo sysctl -w vm.max_map_count=262144
```

## Elastic Stack deployment
As mentioned in the previous section, deployment of the Elastic Stack environment (with two Elasticsearch instances, and one each for Kibana and Logstash) is based on the official Elastic images and in an adaptation of the official Docker Compose files in the [Elastic Github site](https://github.com/elastic/)  (the X-Pack has been disabled according to the [official](https://www.elastic.co/guide/en/x-pack/current/xpack-settings.html) [documentation](https://www.elastic.co/guide/en/x-pack/current/installing-xpack.html#xpack-enabling)). Logstash is installed to enable integration scenarios where the results of Spark processing are not directly written to Elasticsearch but through CSV files. Thus, the following steps have to be followed:

A directory for the Docker Compose YAML file and other auxiliary files is created:

```bash
mkdir /home/ubuntu/elk
```

Folders for Logstash are created as well (the `pipeline` folder contains the configuration files for Logstash; `input` is created to contain files that can be processed by Logstash):

```bash
mkdir -p /home/ubuntu/elk/logstash/pipeline
mkdir /home/ubuntu/elk/logstash/input
```

The followind YAML file is used by Docker Compose. As with `docker_install.sh`, this `docker-compose.yml` file is available in the `elastic` folder in the Github repo:
```yaml
version: '2'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:5.6.0
    container_name: elasticsearch
    restart: on-failure
    environment:
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
      - xpack.monitoring.enabled=false
      - xpack.graph.enabled=false
      - xpack.watcher.enabled=false
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    mem_limit: 2g
    cap_add:
      - IPC_LOCK
    volumes:
      - esdata1:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
  elasticsearch2:
    image: docker.elastic.co/elasticsearch/elasticsearch:5.6.0
    restart: on-failure
    environment:
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - "discovery.zen.ping.unicast.hosts=elasticsearch"
      - xpack.security.enabled=false
      - xpack.monitoring.enabled=false
      - xpack.graph.enabled=false
      - xpack.watcher.enabled=false
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    mem_limit: 2g
    cap_add:
      - IPC_LOCK
    volumes:
      - esdata2:/usr/share/elasticsearch/data
  kibana:
    image: docker.elastic.co/kibana/kibana:5.6.0
    container_name: kibana
    volumes:
      - ./kibana.yml:/usr/share/kibana/config/kibana.yml
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
  logstash:
    image: docker.elastic.co/logstash/logstash:5.6.0
    container_name: logstash
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logstash/input:/tmp
    environment:
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=false
      - xpack.monitoring.enabled=false
      - xpack.graph.enabled=false
      - xpack.watcher.enabled=false
    ports:
      - "5001:5000"
    depends_on:
      - elasticsearch
volumes:
  esdata1:
    driver: local
  esdata2:
    driver: local
```

Some aspect to remark:
* Storage in Elasticsearch is persistent, as two volumes in the host machine, handled by Docker, are used: ```/var/lib/docker/volumes/elk_esdata1/``` and ```/var/lib/docker/volumes/elk_esdata2/```. That is, although the containers are stopped, storage is kept. The volume contents can be erased by removing the volumes (`docker volume rm elk_esdata1` and `docker volume rm elk_esdata2`).
* Three ports are exposed so that it is possible to interact with the components of the Elastic Stack: 9200 for Elasticsearch, 5601 for Kibana and 5001 for Logstash (that is, `<elk-floating-ip-address>:9200`, `<elk-floating-ip-address>:5601` and `<elk-floating-ip-address>:5001`).

A `kibana.yml` is needed as well. The following file, also available in the `elastic` folder of the Github repo, can be used:
```yaml
xpack.security.enabled: "false"
xpack.monitoring.enabled: "false"
xpack.graph.enabled: "false"
xpack.watcher.enabled: "false"

http.cors.allow-origin: "/.*/"
http.cors.enabled: true

server.port: 5601
server.host: 0.0.0.0

elasticsearch.url: http://elasticsearch:9200
```
Thus, the folder structure in the Elastic Stack instance will be as follows (from `/home/ubuntu`):
```bash
.
+-- elk
    +-- docker-compose.yml
    +-- kibana.yml
    +-- logstash
        +-- input
        +-- pipeline
```

Finally, the Elastic Stack infrastructure can be started by executing the following commands:
```bash
cd /home/ubuntu/elk
docker-compose up -d
```

The result should be similar to this:
```bash
Creating network "elk_default" with the default driver
Creating volume "elk_esdata2" with local driver
Creating volume "elk_esdata1" with local driver
Creating elk_elasticsearch2_1 ...
Creating elasticsearch ...
Creating elk_elasticsearch2_1
Creating elasticsearch ... done
Creating kibana ...
Creating logstash ...
Creating kibana
Creating logstash ... done
```

## Elasticsearch index definition

## Spark configuration