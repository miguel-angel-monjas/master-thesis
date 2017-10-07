##Kafka deployment
`docker run -d -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=10.10.10.66 --env ADVERTISED_PORT=9092 spotify/kafka`

`docker run -it --rm --link 1195a74812a6 spotify/kafka /opt/kafka_2.11-0.10.1.0/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic cdr --from-beginning`

## Kafka installation and configuration at the Spark cluster
`conda install -c conda-forge kafka-python`

`pyspark --master spark://cluster-master:7077 --executor-memory 24G --driver-memory 10G --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2`

spark -> /opt/sparks/spark-1.6.2-bin-hadoop2.6/

ln -s /opt/sparks/spark-2.0.2-bin-hadoop2.7/ spark/
