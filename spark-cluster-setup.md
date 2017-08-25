# Running Spark on a YARN cluster
In [Setting up a Hadoop cluster](./spark-cluster-management.md) we described how to set up a YARN-enabled Hadoop cluster. It is made of a master node (hosting an HDFS *NameNode* and a YARN "ResourceManager") and two slaves (running each an HDFS *DataNode* and a YARN *NodeManager*; the master node hosts a *DataNode* and a "NodeManager* as well). Here, we will describe how to set up a Spark cluster with Jupyter Notebook support on the Hadoop cluster.

## Install Spark on all instances
We choose a Spark release compatible with Hadoop 2.7.4: [Spark 2.1.1](https://spark.apache.org/releases/spark-release-2-1-1.html).

```bash
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.1.1-bin-hadoop2.7.tgz
tar -zxvf spark-2.1.1-bin-hadoop2.7.tgz
sudo mv spark-2.1.1-bin-hadoop2.7 /usr/local/spark
rm spark-2.1.1-bin-hadoop2.7.tgz
```

## Setup Spark environment variables on master and slave nodes
we set the variables in the `.bashrc` file under `/home/ubuntu`. Do it on master and slave nodes:
```bash
echo '
# Set SPARK_HOME
export SPARK_HOME=/usr/local/spark
# Add Spark bin directory to PATH
export PATH=$PATH:$SPARK_HOME/bin
' >> ~/.bashrc
```

Reload the `.bashrc` file:
```bash
source ~/.bashrc
```

Next, activate and set some variables in the `spark-env.sh` configuration file on master and slave nodes:
```bash
cp $SPARK_HOME/conf/spark-env.sh.template $SPARK_HOME/conf/spark-env.sh
echo '
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export SPARK_MASTER_IP=10.65.104.210
' >> $SPARK_HOME/conf/spark-env.sh
```

Finally, the Spark `slaves` file is updated, only on the master node:
```bash
echo "
cluster-master
hsdf-slave-1
hdsf-slave-2
" >> $SPARK_HOME/conf/slaves
```

## See also
* [Setting up a Hadoop cluster](./hadoop-cluster-setup.md)
* [Deploying YARN on a Hadoop cluster](./yarn-clusters-setup.md)
