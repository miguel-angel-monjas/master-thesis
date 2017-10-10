#Setting up Kafka
Apache Kafka is a distributed publish-subscribe messaging system that is designed to be fast, scalable, and durable. Kafka maintains feeds of messages in so-called topics. Producers write data to topics and consumers read from topics. These guidelines will support a scenario where Kafka is used to to provide inputs to Spark Streaming applications and to deliver the outputs of said applications to Elasticsearch, so that they can be visualized.

----
## Pre-requisites
The deployment of Kafka on an Openstack instance will be carried out by means of Docker containers. Thus, Docker CE and Docker Compose have to be installed before the containers can be created. It can be done by executing [`docker_install.sh`](https://github.com/miguel-angel-monjas/master-thesis/blob/master/elastic/docker_install.sh), a shell script availabe in the `elastic` folder in the Github repo. 

##Kafka deployment
The deployment of Kafka on an Openstack instance is carried out by using a Docker container that runs the ubiquitous [`spotify/kafka`](https://hub.docker.com/r/spotify/kafka/) image. The following command can be run:
`docker run -d -p 2181:2181 -p 9092:9092 --name kafka_container --env ADVERTISED_HOST=<kafka-ip-address> --env ADVERTISED_PORT=9092 spotify/kafka`

Successful execution of Kafka can be verified by checking whether it is one of the running containers (`docker ps`) or by inspecting the container logs (`docker logs kafka_container`). Once producers start pushing messages to Kafka under the `topic_name` topic, it is possible to read them by executing, from the Kafka host, the following command:

`docker run -it --rm --link kafka_container spotify/kafka /opt/kafka_2.11-0.10.1.0/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic <topic_name> --from-beginning`

There is another possibility if no extra instance for Kafka is wished. Instead of running Kafka on its own instance, it can be run in the Elastic Stack instance. A `kafka` service can be added to the `docker-compose.yml` file:

```yaml
  kafka:
    image: spotify/kafka
    environment:
      - ADVERTISED_HOST=10.10.10.66
      - ADVERTISED_PORT=9092
      - AUTO_CREATE_TOPICS=true
      - NUM_PARTITIONS=1
    ports:
      - "9092"
    networks:
      - elk
    container_name: kafka_container
```

## Kafka installation and configuration at the Spark cluster
As with the Elastic Stack case, interworking with Kafka from Spark Streaming applications require a specific connector, [Spark Integration For Kafka 0.8](https://mvnrepository.com/artifact/org.apache.spark/spark-streaming-kafka-0-8_2.11/2.0.2). The connector binaries must be added to the driver and executor classpaths by means of the `--packages` option:

`pyspark --master spark://<master-ip-address>:7077 --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2`

It is also possible to download the jar file and copy it to the `$SPARK_HOME/jars` folder.


