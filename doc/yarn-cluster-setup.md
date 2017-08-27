# Deploying YARN on a Hadoop cluster
In [Setting up a Hadoop cluster](./hadoop-cluster-setup.md) a description on how to set up a Hadoop cluster was provided. It is made of a master node (hosting an HDFS *NameNode* and a HDFS "DataNode") and two slaves (running each an HDFS *DataNode*). Here you have a description on how to deploy YARN on top of it.

## Cluster instances configurations
Assuming that the HDFS cluster is already running, two additional files have to be updated (or created) on master and slave instances in order to deploy YARN on the cluster: `mapred-site.xml` and `yarn-site.xml` (mind that some variables have been deprecated as new versions of Hadoop come out). As with the HDFS cluster, the files are in the directory `$HADOOP_CONF_DIR`. Although there are some options that are only relevant for the master, it is simpler to copy the same configuration files to all the instances in the cluster.

### `mapred-site.xml`
`mapred-site.xml` must be created on the master node in order to activate YARN by setting the `mapreduce.framework.name` property. Default property values can be found [here](https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml):
```bash
cp $HADOOP_CONF_DIR/mapred-site.xml.template $HADOOP_CONF_DIR/mapred-site.xml
nano $HADOOP_CONF_DIR/mapred-site.xml
```
```xml
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
    <description>The framework for running mapreduce jobs</description>
  </property>
</configuration>
```

### `yarn-site.xml`
`yarn-site.xml` is the responsible of YARN cluster configuration and must be updated on master and slave nodes in order to:
* Activate properties related to the *ResourceManager* ports so that the different entities connect properly to each other.
* Set the property `yarn.nodemanager.aux-services`. 
* Enable all interfaces are listened to. Otherwise, connection between nodes will not be possible (it follows a similar pattern to plain Hadoop configuration)
* Dimension the YARN cluster.

The YARN *ResourceManager* implements three different schedulers. At the moment, the default option (*Capacity Scheduler*, configured via `yarn.resourcemanager.scheduler.class`) is kept.

Default values can be found [here](https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-common/yarn-default.xml).

```bash
nano $HADOOP_CONF_DIR/yarn-site.xml
```
```xml
<configuration>
  <property>
    <name>yarn.resourcemanager.scheduler.address</name>
    <value>cluster-master:8030</value>
  </property> 
  <property>
    <name>yarn.resourcemanager.address</name>
    <value>cluster-master:8032</value>
  </property>
  <property>
    <name>yarn.resourcemanager.webapp.address</name>
    <value>cluster-master:8088</value>
  </property>
  <property>
    <name>yarn.resourcemanager.resource-tracker.address</name>
    <value>cluster-master:8031</value>
  </property>
  <property>
    <name>yarn.resourcemanager.admin.address</name>
    <value>cluster-master:8033</value>
  </property>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.resourcemanager.bind-host</name>
    <value>0.0.0.0</value>
  </property>
  <property>
    <name>yarn.nodemanager.bind-host</name>
    <value>0.0.0.0</value>
  </property>
  <property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>20480</value>
  </property> 
  <property>
    <name>yarn.nodemanager.resource.cpu-vcores</name>
    <value>28</value>
  </property>
</configuration>
```

It is important to note that specific values must be set for the properties `yarn.nodemanager.resource.memory-mb` and `yarn.nodemanager.resource.cpu-vcores`. 
* `yarn.nodemanager.resource.memory-mb`. It is the amount of physical memory, in MB, that can be allocated for containers. As the instances’ RAM in the considered environment is 32GB, it can be considered that about 8GB are used by the operating system and other tasks, 1GB each for the HDFS *DataNode* and the YARN *NodeManager*, so that 22GB can be a good fit (the master instance should consider also the HDFS *NameNode* and the YARN *ResourceManager* and provide about 20 GB instead). Default value is 8192.
* `yarn.nodemanager.resource.cpu-vcores`. It is the number of vcores that can be allocated for containers. As the instances have 32 vCPU's, and considering that the operating system uses one of them and one each for the HDFS *DataNode* and the YARN *NodeManager*, 29 seems to be a good choice (27 is used in the master). Default value is 8.

Although not followed, [the official Cloudera documentation on YARN tuning](https://www.cloudera.com/documentation/enterprise/5-3-x/topics/cdh_ig_yarn_tuning.html) can provide an overview of the optimization of YARN clusters. In fact, if proper values of the properties above are not set, *NodeManagers* will not be authorized to register and the cluster will not be deployed.

## YARN start
Start YARN once the Distributed File System has been already started:

```bash
$HADOOP_HOME/sbin/start-yarn.sh
```

The output of jps should list `NodeManager` and `ResourceManager` on the master node (besides the processes related to plain Hadoop):
```bash
17089 DataNode
16947 NameNode
18516 NodeManager
18375 ResourceManager
18760 Jps
17324 SecondaryNameNode
```

And `NodeManager` on each slave nodes.
```bash
8006 NodeManager
6507 DataNode
8395 Jps
```

The status of the YARN cluster can be verified in http://cluster-master:8088/

To stop the YARN cluster, simply type:
```bash
$HADOOP_HOME/sbin/stop-yarn.sh
```

It is possible to start (and stop) both the DFS and the YARN daemons, by using `$HADOOP_HOME/sbin/start-all.sh` and `$HADOOP_HOME/sbin/stop-all.sh` but a warning states that such scripts are deprecated.

## Key take-aways
Some considerations when setting up a Hadoop cluster have been already mentioned. Some of them (binding to all interfaces) apply to the YARN cluster as well. However, new issues arise:
* you have to carefully dimension the cluster. If you use small flavors, *NodeManagers* will not be able to gather enough resources and will be rejected at registration. Thus, you need to use instances with a certain amount of memory and properly configure `yarn.nodemanager.resource.memory-mb` and `yarn.nodemanager.resource.cpu-vcores`.

## See also
* [Setting up a Hadoop cluster](./hadoop-cluster-setup.md)
* [Running Spark on a YARN cluster](./spark-yarn-cluster-setup.md)