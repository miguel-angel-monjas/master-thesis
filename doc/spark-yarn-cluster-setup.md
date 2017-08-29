# Running Spark on a YARN cluster
In [Deploying YARN on a Hadoop cluster](./yarn-cluster-setup.md) we described how to set up a YARN-enabled Hadoop cluster. It is made of a master node (hosting an HDFS *NameNode* and a YARN *ResourceManager*) and two slaves (running each an HDFS *DataNode* and a YARN *NodeManager*; the master node hosts a *DataNode* and a *NodeManager* as well). Here, we will describe how to set up a Spark cluster with Jupyter Notebook support on the Hadoop cluster.

* [Spark installation on all instances](#spark-installation-on-all-instances)
* [Setup Spark environment variables on master and slave nodes](#setup-spark-environment-variables-on-master-and-slave-nodes)
* [See also](#see-also)

----

## Spark installation on all instances
We choose a Spark release compatible with Hadoop 2.7.4: [Spark 2.0.2](https://spark.apache.org/releases/spark-release-2-0-2.html).

```bash
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.0.2-bin-hadoop2.7.tgz
tar -zxvf spark-2.0.2-bin-hadoop2.7.tgz
sudo mv spark-2.0.2-bin-hadoop2.7 /usr/local/spark
rm spark-2.0.2-bin-hadoop2.7.tgz
```

## Setup Spark environment variables on master and slave nodes
The following environment variables are set in the `.bashrc` file under `/home/ubuntu` (both on master and slave nodes):
```bash
echo '
# Set SPARK_HOME
export SPARK_HOME=/usr/local/spark
# Add Spark bin directory to PATH
export PATH=$PATH:$SPARK_HOME/bin
' >> ~/.bashrc
```

The `.bashrc` file is reloaded:
```bash
source ~/.bashrc
```

Next, activate and set some variables in the `spark-env.sh` configuration file on master and slave nodes:
```bash
cp $SPARK_HOME/conf/spark-env.sh.template $SPARK_HOME/conf/spark-env.sh
echo '
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export SPARK_MASTER_IP=<master-ip-address>
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
* [Deploying YARN on a Hadoop cluster](./yarn-cluster-setup.md)
