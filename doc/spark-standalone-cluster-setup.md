# Running a Spark cluster in stand-alone mode
In [Setting up a Hadoop cluster](./hadoop-cluster-setup.md) a description on how to set up a Hadoop cluster was provided. It is made of a master node (hosting an HDFS *NameNode* and a HDFS "DataNode") and two slaves (running an HDFS *DataNode* each). Here, a description on e how to deploy a Spark cluster in stand-alone mode on top of it is provided. As YARN is not used, no dependencies between the Hadoop and the Spark clusters will exist and Hadoop will simply provide storage capabilities. The official documentation can be accessed [here](https://spark.apache.org/docs/latest/spark-standalone.html).

## Pre-requisites
Hadoop 2.7.4 is installed and a cluster is set up as described in [Setting up a Hadoop cluster](./spark-cluster-management.md).

## Spark installation on all instances
A Spark release compatible with Hadoop 2.7.4, [Spark 2.1.1](https://spark.apache.org/releases/spark-release-2-1-1.html), is chosen.

```bash
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.1.1-bin-hadoop2.7.tgz
tar -zxvf spark-2.1.1-bin-hadoop2.7.tgz
sudo mv spark-2.1.1-bin-hadoop2.7 /usr/local/spark
rm spark-2.1.1-bin-hadoop2.7.tgz
```

## Spark environment variables setup on master and slave nodes
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

Next, some variables in the `spark-env.sh` configuration file are activated and set on master and slave nodes:
```bash
cp $SPARK_HOME/conf/spark-env.sh.template $SPARK_HOME/conf/spark-env.sh
echo '
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
' >> $SPARK_HOME/conf/spark-env.sh
```

Finally, you can use a not so verbose logging level:
```bash
cp $SPARK_HOME/conf/log4j.properties.template $SPARK_HOME/conf/log4j.properties
sed -i 's/log4j.rootCategory=INFO, console/log4j.rootCategory=WARN, console/' $SPARK_HOME/conf/log4j.properties
```

## Spark cluster slaves configuration
The Spark `slaves` file must be updated, only on the master node. Notice it has the same contents as the Hadoop `slaves` file.
```bash
echo "
cluster-master
cluster-slave-1
cluster-slave-2
" >> $SPARK_HOME/conf/slaves
```

## Cluster start
In the master:
```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slaves.sh 
``` 
Instead, it is possible start *Master* and *Workers* at the same time:
```bash
$SPARK_HOME/sbin/start-all.sh 
``` 

To validate it has started successfully, `jps` can be run on the master and slave instances. The output should list `Worker` and` Master` on the master node:
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

## Jupyter Notebook installation
An Anaconda Python distribution is installed on master and slave instances:

```bash
wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh
sudo /bin/bash Anaconda2-4.2.0-Linux-x86_64.sh -b -p /usr/local/anaconda
sudo chown -R ubuntu:ubuntu /usr/local/anaconda/
rm Anaconda2-4.2.0-Linux-x86_64.sh
/usr/local/anaconda/bin/conda update -y conda
/usr/local/anaconda/bin/conda install -c conda-forge findspark=1.0.0 -y
/usr/local/anaconda/bin/jupyter notebook --generate-config -y
```

Next, the following environment variables must be set in the `.bashrc` file under `/home/ubuntu` (both on master and slave nodes):
```bash
echo '
# Set ANACONDA_HOME
export ANACONDA_HOME=/usr/local/anaconda
# Add Anaconda bin directory to PATH
export PATH=$PATH:$ANACONDA_HOME/bin
' >> ~/.bashrc
```

The `.bashrc` file is reloaded:
```bash
source ~/.bashrc
```

Verify that Python 2.7 has been properly installed by typing `python`. The output should be similar to this:
```bash
Python 2.7.12 |Anaconda custom (64-bit)| (default, Jul  2 2016, 17:42:40)
[GCC 4.4.7 20120313 (Red Hat 4.4.7-1)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
Anaconda is brought to you by Continuum Analytics.
Please check out: http://continuum.io/thanks and https://anaconda.org
>>>
```

Verify that PySpark is properly installed without using Jupyter Notebook first:
```bash
```

## Jupyter Notebook configuration
A folder for notebooks and kernels must be created:
```bash
mkdir ~/notebooks
```

Next, the Jupyter Notebook configuration file, `~/.jupyter/jupyter_notebook_config.py`, must be updated to use the just created folder and for enable the access from external ip addresses to the notebooks:
```bash
sed -i "s/#c.NotebookApp.notebook_dir = u''/c.NotebookApp.notebook_dir = u'\/home\/ubuntu\/notebooks'/" ~/.jupyter/jupyter_notebook_config.py
sed -i "s/#c.NotebookApp.ip = 'localhost'/c.NotebookApp.ip = '*'/" ~/.jupyter/jupyter_notebook_config.py
```

Finally, Spark must be configured 

```bash
pyspark --master spark://<master-ip-address>:7077
````

## See also
* [Running Spark on a YARN cluster](./spark-yarn-cluster-setup.md)
* [Running Spark on a standalone cluster](./spark-standalone-cluster-setup.md)