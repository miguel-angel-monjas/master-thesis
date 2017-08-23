# Creation of a Hadoop cluster   

# Instance creation
We create three instances in the OpenStack cloud: we’ll name them `hdfs-master`, `hdfs-slave-1` and `hdfs-slave-2`. The flavor used has the following features:
* **Memory**: 32 GB
* **vCPU**: 32

The image used is Ubuntu 16.06. All of them are provided a floating IP address (in our environment: `10.65.104.210`, `10.65.104.175`, and `10.65.104.176`).

## Install Java on all instances  
```bash
sudo apt-get update
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get install -y oracle-java8-installer
sudo apt-get install -y oracle-java8-set-default
```

## Install Hadoop on all the instances
We choose Hadoop 2.7.4.
```bash
wget http://ftp.cixug.es/apache/hadoop/common/hadoop-2.7.4/hadoop-2.7.4.tar.gz
tar -xvzf hadoop-2.7.4.tar.gz
sudo mv hadoop-2.7.4 /usr/local/hadoop
rm hadoop-2.7.4.tar.gz
```

## Setup Hadoop environment variables on master and slave nodes
In order to determine Java home, we use the following command:
```bash
readlink -f /usr/bin/java | sed "s:bin/java::"
```

Next, we set the variables in the .bashrc file under /home/ubuntu. Do it on master and slave nodes:
```bash
sudo nano ~/.bashrc
```
```bash
# Set HADOOP_HOME
export HADOOP_HOME=/usr/local/hadoop
# Set JAVA_HOME 
export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
# Add Hadoop bin and sbin directory to PATH
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
```

Reload the .bashrc file:
```bash
source ~/.bashrc
```

Finally, we update the $JAVA_HOME variable in the hadoop_env.sh configuration file on master and slave nodes:
```bash
sudo nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```
```bash
#export JAVA_HOME=${JAVA_HOME}
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
```

## Install ssh on all instances
```bash
sudo apt-get update
sudo apt-get install ssh -y
sudo apt-get install rsync -y
```

## Update /etc/hosts in all instances
In the master:
```bash
sudo nano /etc/hosts
```
```bash
10.65.104.210   hdfs-master
10.65.104.175   hdfs-slave-1
10.65.104.176   hdfs-slave-2
```

In the slaves:
```bash
sudo nano /etc/hosts
```
```bash
10.65.104.210   hdfs-master
10.65.104.175   hdfs-slave-1
10.65.104.176   hdfs-slave-2
```

## Enable password-less ssh
Enabling password-less ssh connection between the instances can be tricky, as connections to the instances in the OpenStack cloud cannot be done but using password-less ssh with the private key used to deploy the instance s(inlab). That is, any instance in our OpenStack cloud already accepts ssh connections from clients with the inlab private key. Thus, making the private key available in the master note would be enough (if unsure about security, mind that any user able to connect to any OpenStack instance already have the private key).

Thus, the simplest way to enable the ssh connection is simply to copy the inlab key (with OpenSSH format) to the /home/ubuntu/.ssh folder in the master node (using a secure FTP client). As we are using PuTTY to handle connections (we use a Windows box), a private key with proper OpenSSH format must be obtained from inlab.ppk. It can be done by means of PuTTYgen, by loading the private key and exporting it as an OpenSSH key. The resulting private key will be named id_rsa and subsequently uploaded to the master instance.

Once in the proper file, the file must be given the right permissions:
```bash
chmod 0600 ~/.ssh/id_rsa
```

Finally, the connection can be tested by using the following command (StrictHostKeyChecking=no used to avoid an interactive dialogue in the first connection):
```bash
ssh -o StrictHostKeyChecking=no hdfs-slave-1
ssh -o StrictHostKeyChecking=no hdfs-slave-2
```

If we do not want to leave the private key in the master instance, we can try an alternative schema, using the private key just to get access to the slave instances and removing it afterwards. First, we follow the procedures to handle the inlab private key in the master instance described previously (upload and permissions set). The result will be having a private key with proper permissions in ~/.ssh/id_rsa.

Next, we need to create a new pair of public/private keys (mind the key names) that will be subsequently used to communications between the master and the slaves:
```bash
ssh-keygen -t rsa -P '' -f ~/.ssh/idhdfs_rsa
cat ~/.ssh/idhdfs_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
```

Once created, we need to upload the public key to the slaves by means of ssh-copy-id. 
```bash
ssh-copy-id -i ~/.ssh/idhdfs_rsa.pub hdfs-slave-1
ssh-copy-id -i ~/.ssh/idhdfs_rsa.pub hdfs-slave-2
```

Finally, we delete the inlab private key and rename the newly-created pair of keys so that the default file names are used:
```bash
rm ~/.ssh/id_rsa
mv ~/.ssh/idhdfs_rsa ~/.ssh/id_rsa
mv ~/.ssh/idhdfs_rsa.pub ~/.ssh/id_rsa.pub
```

Verify that seamless ssh connection is enabled by using the command written down in the previous options:
```bash
ssh -o StrictHostKeyChecking=no hdfs-slave-1
ssh -o StrictHostKeyChecking=no hdfs-slave-2
```

## Configure the instances
Five configuration files have to be updated (or created) on master and slave instances in order to have our cluster configured: core-site.xml, mapred-site.xml, hdfs-site.xml, yarn-site.xml, and slaves. (mind that some variables have been deprecated as new versions of Hadoop are releases, be aware of that).

### core-site.xml
First, core-site.xml must be updated on all instances (master and slaves), in order to set the properties hadoop.tmp.dir and fs.defaultFS:
```bash
sudo nano $HADOOP_HOME/etc/hadoop/core-site.xml
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

### mapred-site.xml
Next, mapred-site.xml must be activated on the master node in order to activate mapreduce.framework.name:
```bash
cp $HADOOP_HOME/etc/hadoop/mapred-site.xml.template $HADOOP_HOME/etc/hadoop/mapred-site.xml
sudo nano $HADOOP_HOME/etc/hadoop/mapred-site.xml
```
```xml
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
    <description>The framework for running mapreduce jobs</description>
  </property>
</configuration>
xml

### hdfs-site.xml
hdfs-site.xml must be updated on master and slave nodes in order to activate the properties dfs.replication, dfs.namenode.name.dir, and dfs.datanode.name.dir. It also sets several properties to enable the instances to listen on all interfaces. 
```bash
sudo nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
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
* dfs.replication: it specifies the default block replication. It defines how many machines a single file should be replicated to before it becomes available. If the variable value is set to a value higher than the number of available slaves (actually DataNodes), there will errors. The default value is 3. As we have only two slaves, we set dfs.replication to 2.
* dfs.namenode.name.dir: Directory is used by the NameNode to store its metadata file. Thus, manual creation of the directory om all nodes is required.
* dfs.datanode.name.dir: Directory is used by DataNodes to store its metadata file. Thus, manual creation of the directory om all nodes is required.
```bash
mkdir -p /home/ubuntu/hdfs/namenode
mkdir -p /home/ubuntu/hdfs/datanode
```

### yarn-site.xml
yarn-site.xml must be updated on master and slave nodes in order to:
•	Activate properties related to the ResourceManager ports.
•	Set yarn.nodemanager.aux-services. 
•	Enable all interfaces are listened to.
•	Dimension the YARN cluster.
```bash
sudo nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
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
  </property> </configuration>
```

It is important to note that specific values must be set for the properties yarn.nodemanager.resource.memory-mb and yarn.nodemanager.resource.cpu-vcores. 
* yarn.nodemanager.resource.memory-mb. It is the amount of physical memory, in MB, that can be allocated for containers. As our instances’ RAM is 32GB, we can consider that about 8GB are used by the operating system and other tasks, 1GB each for the HDFS DataNode and the YARN NodeManager, so that 22GB can be a good fit (the master instance should consider also the HDFS NameNode and the YARN ResourceManager and provide about 20 GB instead). Default value is 8192.
* yarn.nodemanager.resource.cpu-vcores. It is the number of vcores that can be allocated for containers. As our instances have 32 vCPU’s, and considering that the operating system uses one of them and one each for the HDFS DataNode and the YARN NodeManager, 29 seems to be a good choice (27 is used in the master). Default value is 8.

### slaves
Finally, the slaves files is updated, only on the master node:
```bash
sudo nano $HADOOP_HOME/etc/hadoop/slaves
```
```bash
hdfs-master
hsdf-slave-1
hdsf-slave-2
```

## Format the HDFS filesystem via the NameNode
(mind that you format again the filesystem in some time in the future, there will be errors related to inconsistent clusterID; datanodes on slave instances will keep the reference to the old namenode and thus you will need to delete and recreate data folders)
```bash
$HADOOP_HOME/bin/hdfs namenode -format
```

## Start the Distributed File System:
Although it is possible to start all daemons at once, it is better to run separately the distributed file system and YARN so that you can verify whether everything is OK:
```bash
$HADOOP_HOME/sbin/start-dfs.sh
```

To validate it has started successfully, you must run jps on the master and slave instances:
```bash
jps
```

The output should list NameNode, SecondaryNameNode, and DataNode on the master node:
```bash
17089 DataNode
16947 NameNode
17324 SecondaryNameNode
17470 Jps
```

And a DataNode in each slave instance.

If you do not get this output in all the instances of the cluster, you need to analyze the log files available at $HADOOP_HOME/logs. Relevant log files are hadoop-ubuntu-datanode-hdfs-master.log, hadoop-ubuntu-namenode-hdfs-master.log, and hadoop-ubuntu-secondarynamenode-hdfs-master.log.

The status of the HDFS cluster can be verified in http://hdfs-master:50070/

To stop the HDFS cluster simply type:
```bash
$HADOOP_HOME/sbin/stop-dfs.sh
```

## Start YARN
```bash
$HADOOP_HOME/sbin/start-yarn.sh
```

The output of jps should list NodeManager and ResourceManager on the master node:
```bash
17089 DataNode
16947 NameNode
18516 NodeManager
18375 ResourceManager
18760 Jps
17324 SecondaryNameNode
```

And NodeManager on each slave nodes.
```bash
8006 NodeManager
6507 DataNode
8395 Jps
```

The status of the YARN cluster can be verified in http://hdfs-master:8088/
To stop the YARN cluster simply type:
```bash
$HADOOP_HOME/sbin/stop-yarn.sh
```

It is possible to start (and stop) both the DFS and the YARN daemons, by using $HADOOP_HOME/sbin/start-all.sh and $HADOOP_HOME/sbin/stop-all.sh but a warning states that they are deprecated.