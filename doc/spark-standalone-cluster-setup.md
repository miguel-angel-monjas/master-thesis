# Running a Spark cluster in stand-alone mode

In [a previous section](./hadoop-cluster-setup.md) we described how to set up a Hadoop cluster. It is made of a master node (hosting an HDFS *NameNode* and a HDFS "DataNode") and two slaves (running an HDFS *DataNode* each). Here, we will describe how to deploy a Spark cluster in stand-alone mode on top of it. As YARN is not used, no dependencies between the Hadoop and the Spark clusters will exist and Hadoop will simply provide storage capabilities. The official documentation can be accessed [here](https://spark.apache.org/docs/latest/spark-standalone.html).

## Pre-requisites
Hadoop 2.7.4 is installed and a cluster is set up as described in [Setting up a Hadoop cluster](./spark-cluster-management.md).

## Install Spark on all instances
We choose a Spark release compatible with Hadoop 2.7.4: [Spark 2.1.1](https://spark.apache.org/releases/spark-release-2-1-1.html).

```bash
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.1.1-bin-hadoop2.7.tgz
tar -zxvf spark-2.1.1-bin-hadoop2.7.tgz
sudo mv spark-2.1.1-bin-hadoop2.7 /usr/local/spark
rm spark-2.1.1-bin-hadoop2.7.tgz
```

## Setup Spark environment variables on master and slave nodes
We set the variables in the `.bashrc` file under `/home/ubuntu`. Do it on master and slave nodes:
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
' >> $SPARK_HOME/conf/spark-env.sh
```

Finally, the Spark `slaves` file is updated, only on the master node. Notice it has the same contents as the Hadoop `slaves` file.
```bash
echo "
cluster-master
cluster-slave-1
cluster-slave-2
" >> $SPARK_HOME/conf/slaves
```

## Start the cluster
In the master
```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slaves.sh 
``` 
Instead, you can start *Master* and *Workers* at the same time:
```bash
$SPARK_HOME/sbin/start-all.sh 
``` 

To validate the cluster has been started successfully, you can run `jps` on the master and slave instances. The output should list `Worker` and` Master` on the master node:
```bash
11512 Worker
10920 Master
11677 Jps
```

And a `Worker` process in each slave instance.

The status of the Spark cluster can be verified in `http://<master-floating-ip-address>:8080/`

To terminate the cluster, you can stop *Master* and *Workers* separately or just with a single command:
```bash
$SPARK_HOME/sbin/stop-master.sh
$SPARK_HOME/sbin/stop-slaves.sh 
``` 
Or:
```bash
$SPARK_HOME/sbin/stop-all.sh 
``` 

## Install Jupyter notebook
```bash
wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh
sudo /bin/bash Anaconda2-4.2.0-Linux-x86_64.sh -b -p /usr/local/anaconda
sudo chown -R ubuntu:ubuntu /usr/local/anaconda/
rm Anaconda2-4.2.0-Linux-x86_64.sh
/usr/local/anaconda/bin/conda update -y conda
/usr/local/anaconda/bin/conda install -c conda-forge findspark=1.0.0 -y
/usr/local/anaconda/bin/jupyter notebook --generate-config -y
```

```bash
echo '
# Set ANACONDA_HOME
export ANACONDA_HOME=/usr/local/anaconda
# Add Anaconda bin directory to PATH
export PATH=$PATH:$ANACONDA_HOME/bin
' >> ~/.bashrc
```

Reload the `.bashrc` file:
```bash
source ~/.bashrc
```

```bash
pyspark --master spark://<master-ip-address>:7077
````

## See also
* [Running Spark on a YARN cluster](./spark-yarn-cluster-setup.md)
* [Running Spark on a standalone cluster](./spark-standalone-cluster-setup.md)