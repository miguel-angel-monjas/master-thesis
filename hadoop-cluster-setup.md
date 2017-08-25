# Setting up a Hadoop cluster
This document is based on [the official Hadoop documentation](https://hadoop.apache.org/docs/r2.7.2/hadoop-project-dist/hadoop-common/ClusterSetup.html) and [other resources found on the Internet](https://chawlasumit.wordpress.com/2015/03/09/install-a-multi-node-hadoop-cluster-on-ubuntu-14-04/). It is important to note that as new releases are available, some properties become deprecated and old tutorials are no longer valid (see the [list of deprecated properties](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/DeprecatedProperties.html)).

The creation of a Hadoop cluster is an intermediate step in the deployment of a Spark cluster. The main reason to require a Hadoop cluster is the size of our datasets, for which a single instance is not enoug.

## Instance creation
We create three instances in the OpenStack cloud: we’ll name them `cluster-master`, `cluster-slave-1` and `cluster-slave-2`. The image used is Ubuntu 16.04 and the flavor (`Spark-Intensive`) has the following features:
* **Memory**: 32 GB
* **vCPU**: 32

All of them are given a private IP address, `<master-ip-address>`, `<slave--ip-address>` and `<slave-2-ip-address>`. We also manually assign a floating IP address to the master instance, `<master-floating-ip-address>` (during setup, slave instances may be also assigned floating ip addresses. They are removed once the cluster is setup.

## Install Java on all instances
We plan to install Oracle Java 8 and follow some tutorial found on the Internet ([here](http://tecadmin.net/install-oracle-java-8-jdk-8-ubuntu-via-ppa/) and [here](http://stackoverflow.com/questions/19275856/auto-yes-to-the-license-agreement-on-sudo-apt-get-y-install-oracle-java7-instal)):

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
We choose [Hadoop 2.7.4](http://hadoop.apache.org/docs/r2.7.4/).
```bash
wget http://ftp.cixug.es/apache/hadoop/common/hadoop-2.7.4/hadoop-2.7.4.tar.gz
tar -xvzf hadoop-2.7.4.tar.gz
sudo mv hadoop-2.7.4 /usr/local/hadoop
rm hadoop-2.7.4.tar.gz
```

## Setup Hadoop environment variables on master and slave nodes
In order to determine the actual Java home, we use the following command:
```bash
readlink -f /usr/bin/java | sed "s:bin/java::"
```

Next, we set the variables in the `.bashrc` file under `/home/ubuntu`. Do it on master and slave nodes:
```bash
echo '
# Set HADOOP_HOME
export HADOOP_HOME=/usr/local/hadoop
# Set JAVA_HOME 
export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
# Add Hadoop bin and sbin directory to PATH
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
' >> ~/.bashrc
```

Reload the `.bashrc` file:
```bash
source ~/.bashrc
```

Finally, we update the `$JAVA_HOME` variable in the `hadoop_env.sh` configuration file on master and slave nodes:
```bash
nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```
```bash
#export JAVA_HOME=${JAVA_HOME}
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
```

## Install ssh on all instances
```bash
sudo apt-get update
sudo apt-get install ssh -y
```

## Update /etc/hosts in all instances
Here it is important to note that private IP addreses must be used (no floating IP addresses are involved here).

```bash
echo "
<master-ip-address>		cluster-master
<slave-1-ip-address>	cluster-slave-1
<slave-2-ip-address>	cluster-slave-2
" | sudo tee --append /etc/hosts
```

## Enable password-less ssh
Enabling password-less ssh connection between the instances can be tricky, as connections to the instances in the OpenStack cloud cannot be done but using password-less ssh with the private key used to deploy the instances (named `inlab`). That is, any instance in our OpenStack cloud already accepts ssh connections from clients with the inlab private key. Thus, making the private key available in the master note would be enough (if unsure about security, mind that any user able to connect to any OpenStack instance already have the private key).

Thus, the simplest way to enable the ssh connection is simply to copy the inlab key (with OpenSSH format) to the `/home/ubuntu/.ssh` folder in the master node (using a secure FTP client). As we are using PuTTY to handle connections (we use a Windows box), a private key with proper OpenSSH format must be obtained from `inlab.ppk`. It can be done by means of PuTTYgen, by loading the private key and exporting it as an OpenSSH key. The resulting private key will be named `id_rsa` and subsequently uploaded to the master instance.

Once in the proper file, the file must be given the right permissions:
```bash
chmod 0600 ~/.ssh/id_rsa
```

Finally, the connection can be tested by using the following command (`StrictHostKeyChecking=no` can be used to avoid an interactive dialogue in the first connection):
```bash
ssh -o StrictHostKeyChecking=no cluster-slave-1
ssh -o StrictHostKeyChecking=no cluster-slave-2
```

If we do not want to leave the private key in the master instance, we can try an alternative schema, using the private key just to get access to the slave instances and removing it afterwards. First, we follow the procedures to handle the inlab private key in the master instance described previously (upload and permissions set). The result will be having a private key with proper permissions in `~/.ssh/id_rsa`.

Next, we need to create a new pair of public/private keys (mind the key names in order not to overwrite the existing key) that will be subsequently used to communications between the master and the slaves:
```bash
ssh-keygen -t rsa -P '' -f ~/.ssh/idhdfs_rsa
cat ~/.ssh/idhdfs_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
```

Once created, we need to upload the public key to the slaves by means of `ssh-copy-id`. 
```bash
for x in cluster-slave-1 cluster-slave-2; ssh-copy-id -i ~/.ssh/idhdfs_rsa.pub $x; done
```

Finally, we delete the `inlab` private key (`id_rsa`) and rename the newly-created pair of keys so that the default file names are used:
```bash
rm ~/.ssh/id_rsa
mv ~/.ssh/idhdfs_rsa ~/.ssh/id_rsa
mv ~/.ssh/idhdfs_rsa.pub ~/.ssh/id_rsa.pub
```

Verify that seamless ssh connection is enabled by using the commands suggested in the previous alternative:
```bash
ssh -o StrictHostKeyChecking=no cluster-slave-1
ssh -o StrictHostKeyChecking=no cluster-slave-2
```

## Configure the cluster instances
Three configuration files have to be updated on master and slave instances in order to have our cluster configured: `core-site.xml`, `hdfs-site.xml`, and `slaves` (mind that some variables have been deprecated as new versions of Hadoop are released, be aware of that). They are available in the directory `$HADOOP_HOME/etc/hadoop`. Although there are some options that are only relevant for the master, it is simpler to copy the same configuration files to all the instances in the cluster.

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
     <value>hdfs://cluster-master:9000</value>
    <description>Use HDFS as file storage engine</description>
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

### `slaves`
Finally, the `slaves` file is updated, only on the master node:
```bash
echo "
cluster-master
hsdf-slave-1
hdsf-slave-2
" >> $HADOOP_HOME/etc/hadoop/slaves
```

## Format the HDFS filesystem via the *NameNode*
(mind that you format again the filesystem in some time in the future, there will be errors related to inconsistent clusterID; *DataNodes* on slave instances will keep the reference to the old *NameNode* and thus you will need to delete and recreate data folders)
```bash
$HADOOP_HOME/bin/hdfs namenode -format
```

## Start the Distributed File System
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

If you do not get this output in all the instances of the cluster, you need to analyze the log files available at `$HADOOP_HOME/logs`. Relevant log files are `hadoop-ubuntu-datanode-cluster-master.log`, `hadoop-ubuntu-namenode-cluster-master.log`, and `hadoop-ubuntu-secondarynamenode-cluster-master.log`.

The status of the HDFS cluster can be verified in http://cluster-master:50070/

To stop the HDFS cluster simply type:
```bash
$HADOOP_HOME/sbin/stop-dfs.sh
```

## Key take-aways

Although works such as *Spark in action* (Manning, 2017) state that "The installation [of YARN and Hadoop] is straightforward", it is not actually true. We have found several issues when setting up the Hadoop cluster. If you have a similar environment to the one described here (OpenStack cloud with Ubuntu 16.06 instances), you shouldn't have any problem following the instructions. However, it is important to focus on the main stoppers we have found:
*  password-less ssh is easy to implement provided that you can copy the keys to all the cluster instances. As we are deploying it in an OpenStack cloud that follows exactly the same principle, uploading a suitable key to the slaves can be tricky. We recommend the second alternative (using a specific pair of keys for enabling cluster communication) described above as it exposes the master key just for a while.
* when only one network interface is in place, you don't have to worry about listening to several interfaces. However, OpenStack creates several interfaces and therefore if you wish to enable binding from any interface, related properties have to be set to 0.0.0.0 (all addresses on the local machine).

## See also
* [Deploying YARN on a Hadoop cluster](./yarn-clusters-setup.md)
* [Running Spark on a YARN cluster](./spark-cluster-setup.md)