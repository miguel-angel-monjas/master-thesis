# Deploying YARN on a Hadoop cluster
In [Setting up a Hadoop cluster](./spark-cluster-management.md) we described how to set up a Hadoop cluster. It is made of a master node (hosting an HDFS *NameNode* and a HDFS "DataNode") and two slaves (running each an HDFS *DataNode*). Here, we will describe how to deploy YARN on top of it.

## Configure the cluster instances
Five configuration files have to be updated (or created) on master and slave instances in order to have our cluster configured: `core-site.xml`, `mapred-site.xml`, `hdfs-site.xml`, `yarn-site.xml`, and `slaves` (mind that some variables have been deprecated as new versions of Hadoop are releases, be aware of that). They are available in the directory `$HADOOP_HOME/etc/hadoop`. Although there are some options that are only relevant for the master, it is simpler to copy the same configuration files to all the instances in the cluster.

### `core-site.xml`
First, `core-site.xml` must be updated on all instances (master and slaves), in order to set the properties `hadoop.tmp.dir` and `fs.defaultFS`:
```bash
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```
```xml
<configuration>
  <property>
    <name>hadoop.tmp.dir</name>
    <value>file:///usr/local/hadoop/tmp</value>
    <description>Temporary Directory.</description>
  </property>
  <property>
    <name>fs.defaultFS</name>
     <value>hdfs://hdfs-master:9000</value>
    <description>Use HDFS as file storage engine</description>
  </property>
</configuration>
```

### `mapred-site.xml`
Next, `mapred-site.xml` must be activated on the master node in order to activate `mapreduce.framework.name`. Default values can be found [here](https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml):
```bash
cp $HADOOP_HOME/etc/hadoop/mapred-site.xml.template $HADOOP_HOME/etc/hadoop/mapred-site.xml
nano $HADOOP_HOME/etc/hadoop/mapred-site.xml
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

### `hdfs-site.xml`
`hdfs-site.xml` must be updated on master and slave nodes in order to activate the properties `dfs.replication`, `dfs.namenode.name.dir`, and `dfs.datanode.name.dir`. It also sets several properties to enable the instances to listen on all interfaces (otherwise, the instances will not be able to connect to each other). See the [official guidelines for HDFS multihoming environments](https://hadoop.apache.org/docs/r2.8.0/hadoop-project-dist/hadoop-hdfs/HdfsMultihoming.html#Ensuring_HDFS_Daemons_Bind_All_Interfaces). Default values can be found [here](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml):
```bash
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```
```xml
<configuration>
<property>
  <name>dfs.replication</name>
    <value>2</value>
    <description>Default block replication.
    The actual number of replications can be specified when the 
    file is created. The default is used if replication is not 
    specified in create time.
    </description>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///home/ubuntu/hdfs/namenode</value>
    <description>Determines where on the local filesystem the DFS 
    name node should store the name table(fsimage). If this is a 
    comma-delimited list of directories then the name table is 
    replicated in all of the directories, for redundancy.
    </description>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///home/ubuntu/hdfs/datanode</value>
    <description>Determines where on the local filesystem an DFS data 
    node should store its blocks. If this is a comma-delimited list 
    of directories, then data will be stored in all named 
    directories, typically on different devices. Directories that do 
    not exist are ignored.
    </description>
  </property>
  <property>
    <name>dfs.namenode.rpc-bind-host</name>
    <value>0.0.0.0</value>
    <description>The actual address the RPC server will bind to. If 
    this optional address is set, it overrides only the hostname 
    portion of dfs.namenode.rpc-address. It can also be specified per 
    name node or name service for HA/Federation. This is useful for 
    making the name node listen on all interfaces by setting it to 
    0.0.0.0.
    </description>
  </property>
  <property>
    <name>dfs.namenode.servicerpc-bind-host</name>
    <value>0.0.0.0</value>
    <description>The actual address the service RPC server will bind 
    to. If this optional address is set, it overrides only the 
    hostname portion of dfs.namenode.servicerpc-address. It can also 
    be specified per name node or name service for HA/Federation. 
    This is useful for making the name node listen on all interfaces 
    by setting it to 0.0.0.0.
    </description>
  </property>
  <property>
    <name>dfs.namenode.http-bind-host</name>
    <value>0.0.0.0</value>
    <description>The actual address the HTTP server will bind to. If 
    this optional address is set, it overrides only the hostname 
    portion of dfs.namenode.http-address. It can also be specified 
    per name node or name service for HA/Federation. This is useful 
    for making the name node HTTP server listen on all interfaces by 
    setting it to 0.0.0.0.
    </description>
  </property>
  <property>
    <name>dfs.namenode.https-bind-host</name>
    <value>0.0.0.0</value>
    <description>The actual address the HTTPS server will bind to. If 
    this optional address is set, it overrides only the hostname 
    portion of dfs.namenode.https-address. It can also be specified 
    per name node or name service for HA/Federation. This is useful 
    for making the name node HTTPS server listen on all interfaces by 
    setting it to 0.0.0.0.
    </description>
  </property>
</configuration>
```

Some remarks about the variables:
* `dfs.replication`: it specifies the default block replication. It defines how many machines a single file should be replicated to before it becomes available. If the variable value is set to a value higher than the number of available slaves (actually *DataNodes*), there will errors. The default value is 3. As we have only two slaves, we set `dfs.replication` to 2.
* `dfs.namenode.name.dir`: Directory is used by the *NameNode* to store its metadata file. Thus, manual creation of the directory on all nodes is required.
* `dfs.datanode.name.dir`: Directory is used by *DataNodes* to store its metadata file. Thus, manual creation of the directory om all nodes is required.

```bash
mkdir -p /home/ubuntu/hdfs/namenode
mkdir -p /home/ubuntu/hdfs/datanode
```

### `yarn-site.xml`
`yarn-site.xml` is the responsible of YARN cluster configuration and must be updated on master and slave nodes in order to:
* Activate properties related to the *ResourceManager* ports so that the different entities connect properly to each other.
* Set `yarn.nodemanager.aux-services`. 
* Enable all interfaces are listened to. Otherwise, connection between nodes will not be possible.
* Dimension the YARN cluster.

The YARN *ResourceManager* implements three different schedulers. At the moment, we will leave the default option (Capacity Scheduler, configured via `yarn.resourcemanager.scheduler.class`).

Default values can be found [here](https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-common/yarn-default.xml).

```bash
nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
```
```xml
<configuration>
  <property>
    <name>yarn.resourcemanager.scheduler.address</name>
    <value>hdfs-master:8030</value>
  </property> 
  <property>
    <name>yarn.resourcemanager.address</name>
    <value>hdfs-master:8032</value>
  </property>
  <property>
    <name>yarn.resourcemanager.webapp.address</name>
    <value>hdfs-master:8088</value>
  </property>
  <property>
    <name>yarn.resourcemanager.resource-tracker.address</name>
    <value>hdfs-master:8031</value>
  </property>
  <property>
    <name>yarn.resourcemanager.admin.address</name>
    <value>hdfs-master:8033</value>
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
* `yarn.nodemanager.resource.memory-mb`. It is the amount of physical memory, in MB, that can be allocated for containers. As our instances’ RAM is 32GB, we can consider that about 8GB are used by the operating system and other tasks, 1GB each for the HDFS *DataNode* and the YARN *NodeManager*, so that 22GB can be a good fit (the master instance should consider also the HDFS *NameNode* and the YARN *ResourceManager* and provide about 20 GB instead). Default value is 8192.
* `yarn.nodemanager.resource.cpu-vcores`. It is the number of vcores that can be allocated for containers. As our instances have 32 vCPU's, and considering that the operating system uses one of them and one each for the HDFS *DataNode* and the YARN *NodeManager*, 29 seems to be a good choice (27 is used in the master). Default value is 8.

Although not followed, [the official Cloudera documentation on YARN tuning](https://www.cloudera.com/documentation/enterprise/5-3-x/topics/cdh_ig_yarn_tuning.html) can provide an overview of the optimization of YARN clusters. In fact, if proper values of the properties above are not set, *NodeManagers* will not be authorized to register and the cluster will not be deployed.

### `slaves`
Finally, the `slaves` file is updated, only on the master node:
```bash
echo "
hdfs-master
hsdf-slave-1
hdsf-slave-2
" >> $HADOOP_HOME/etc/hadoop/slaves
```

## Format the HDFS filesystem via the *NameNode*
(mind that you format again the filesystem in some time in the future, there will be errors related to inconsistent clusterID; *DataNodes* on slave instances will keep the reference to the old *NameNode* and thus you will need to delete and recreate data folders)
```bash
$HADOOP_HOME/bin/hdfs namenode -format
```

## Start the Distributed File System:
Although it is possible to start all daemons at once, it is better to run separately HDFS and YARN so that you can verify whether everything is OK. Scripts for starting and stopping the HDFS and YARN daemons are available in the `$HADOOP_HOME/sbin` folder.

HDSF daemons are started by running, only in the master node:
```bash
$HADOOP_HOME/sbin/start-dfs.sh
```

To validate it has started successfully, you must run `jps` on the master and slave instances. The output should list `NameNode`, `SecondaryNameNode`, and` DataNode` on the master node:
```bash
17089 DataNode
16947 NameNode
17324 SecondaryNameNode
17470 Jps
```

And a `DataNode` in each slave instance.

If you do not get this output in all the instances of the cluster, you need to analyze the log files available at `$HADOOP_HOME/logs`. Relevant log files are `hadoop-ubuntu-datanode-hdfs-master.log`, `hadoop-ubuntu-namenode-hdfs-master.log`, and `hadoop-ubuntu-secondarynamenode-hdfs-master.log`.

The status of the HDFS cluster can be verified in http://hdfs-master:50070/

To stop the HDFS cluster simply type:
```bash
$HADOOP_HOME/sbin/stop-dfs.sh
```

## Start YARN
```bash
$HADOOP_HOME/sbin/start-yarn.sh
```

The output of jps should list `NodeManager` and `ResourceManager` on the master node:
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

The status of the YARN cluster can be verified in http://hdfs-master:8088/

To stop the YARN cluster, simply type:
```bash
$HADOOP_HOME/sbin/stop-yarn.sh
```

It is possible to start (and stop) both the DFS and the YARN daemons, by using `$HADOOP_HOME/sbin/start-all.sh` and `$HADOOP_HOME/sbin/stop-all.sh` but a warning states that they are deprecated.

## Key take-aways

Although works such as *Spark in action* (Manning, 2017) state that "The installation [of YARN and Hadoop] is straightforward", it is not actually true. We have found several issues when setting up the YARN cluster. If you have a similar environment to the one described here (OpenStack cloud with Ubuntu 16.06 instances), you shouldn't have any problem following the instructions. However, it is important to focus on the main stoppers we have found:
*  password-less ssh is easy to implement provided that you can copy the keys to all the cluster instances. As we are deploying it in an OpenStack cloud that follows exactly the same principle, uploading a suitable key to the slaves can be tricky. We recommend the second alternative (using a specific pair of keys for enabling cluster communication) described above as it exposes the master key just for a while.
* when only one network interface is in place, you don't have to worry about listening to several interfaces. However, OpenStack creates several interfaces and therefore if you wish to enable binding from any interface, related properties have to be set to 0.0.0.0 (all addresses on the local machine).
* you have to carefully dimension the cluster. If you use small flavors, *NodeManagers* will not be able to gather enough resources and will be rejected at registration. Thus, you need to use instances with a certain amount of memory and properly configure `yarn.nodemanager.resource.memory-mb` and `yarn.nodemanager.resource.cpu-vcores`.

## See also
* [Running Spark on YARN](./spark-cluster-management.md)