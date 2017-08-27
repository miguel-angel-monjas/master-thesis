# Setting up a Hadoop cluster
This document is based on [the official Hadoop documentation](https://hadoop.apache.org/docs/r2.7.2/hadoop-project-dist/hadoop-common/ClusterSetup.html) and [other resources found on the Internet](https://chawlasumit.wordpress.com/2015/03/09/install-a-multi-node-hadoop-cluster-on-ubuntu-14-04/). It is important to note that as new releases come out, some properties become deprecated and old tutorials are no longer valid (see the [list of deprecated properties](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/DeprecatedProperties.html)).

The creation of a Hadoop cluster is an intermediate step in the deployment of a Spark cluster. The main reason to require a Hadoop cluster is the size of the datasets, for which a single instance is not enough.

## Instance creation
Three instances are created in the OpenStack cloud: the following hostnames will be assigned `cluster-master`, `cluster-slave-1` and `cluster-slave-2`. The image used is Ubuntu 16.04 and the flavor (`Spark-Intensive`) has the following features:
* **Memory**: 32 GB
* **vCPU**: 32

All of them are given a private IP address, `<master-ip-address>`, `<slave--ip-address>` and `<slave-2-ip-address>`. A floating IP address must be manually assigned to the master instance: `<master-floating-ip-address>` (during setup, slave instances may be also assigned floating ip addresses; they will be removed once the cluster is setup).

## Java installation on all instances
Oracle Java 8 is installed. Some tutorials found on the Internet ([here](http://tecadmin.net/install-oracle-java-8-jdk-8-ubuntu-via-ppa/) and [here](http://stackoverflow.com/questions/19275856/auto-yes-to-the-license-agreement-on-sudo-apt-get-y-install-oracle-java7-instal)) are used:

```bash
sudo apt-get update
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get install -y oracle-java8-installer
sudo apt-get install -y oracle-java8-set-default
```

## Hadoop installation on all the instances
[Hadoop 2.7.4](http://hadoop.apache.org/docs/r2.7.4/) is chosen:
```bash
wget http://ftp.cixug.es/apache/hadoop/common/hadoop-2.7.4/hadoop-2.7.4.tar.gz
tar -xvzf hadoop-2.7.4.tar.gz
sudo mv hadoop-2.7.4 /usr/local/hadoop
rm hadoop-2.7.4.tar.gz
```

## Hadoop environment variables setup on master and slave nodes
In order to determine the actual Java home, the following command is used:
```bash
readlink -f /usr/bin/java | sed "s:bin/java::"
```

Next, the following environment variables are set in the `.bashrc` file under `/home/ubuntu` (both on master and slave nodes):
```bash
echo '
# Set HADOOP_HOME
export HADOOP_HOME=/usr/local/hadoop
# Set HADOOP_CONF_DIR
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
# Set $HADOOP_LOG_DIR
export HADOOP_LOG_DIR=$HADOOP_HOME/logs
# Set JAVA_HOME 
export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
# Add Hadoop bin and sbin directory to PATH
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
' >> ~/.bashrc
```

The `.bashrc` file is reloaded:
```bash
source ~/.bashrc
```

Finally, the `$JAVA_HOME` variable is updated in the `hadoop_env.sh` configuration file on master and slave nodes:

```bash
sed -i 's/export JAVA_HOME=${JAVA_HOME}/#export JAVA_HOME=${JAVA_HOME}\nexport JAVA_HOME=$(readlink -f \/usr\/bin\/java | sed "s:bin\/java::")/' $HADOOP_CONF_DIR/hadoop-env.sh
```

## ssh installation on all instances
```bash
sudo apt-get update
sudo apt-get install ssh -y
```

## /etc/hosts update in all instances
Here it is important to note that private IP addreses must be used (no floating IP addresses are involved here).

```bash
echo "
<master-ip-address>		cluster-master
<slave-1-ip-address>	cluster-slave-1
<slave-2-ip-address>	cluster-slave-2
" | sudo tee --append /etc/hosts
```

## Password-less ssh setup
Enabling password-less ssh connection between the instances can be tricky, as connections to the instances in the OpenStack cloud cannot be done but using password-less ssh with the private key used to deploy the instances (named `lab`). That is, any instance in the considered OpenStack cloud already accepts ssh connections from clients with the `lab` private key. Thus, making the private key available in the master note would be enough (if unsure about security, mind that any user able to connect to any OpenStack instance already have the private key).

Thus, the simplest way to enable the ssh connection is simply to copy the `lab` key (with OpenSSH format) to the `/home/ubuntu/.ssh` folder in the master node (using any secure FTP client). As you were using PuTTY to handle connections, a private key with proper OpenSSH format would have to be obtained from `lab.ppk`. It can be done by means of PuTTYgen, by loading the private key and exporting it as an OpenSSH key. The resulting private key will be named `id_rsa` and subsequently uploaded to the master instance.

Once in the proper folder, the key file must be given the right permissions:
```bash
chmod 0600 ~/.ssh/id_rsa
```

Finally, the connection can be tested by using the following command (`StrictHostKeyChecking=no` can be used to avoid an interactive dialogue in the first connection):
```bash
ssh -o StrictHostKeyChecking=no cluster-slave-1
ssh -o StrictHostKeyChecking=no cluster-slave-2
```

If you do not wish to leave the private key in the master instance, an alternative schema can be used. It uses the cloud private key just to get access to upload a new key to the slave instances. Once done, the cloud private key is removed. First, the procedures to handle the `lab` private key in the master instance described previously (upload and permissions set) are followed. The result will be having a private key with proper permissions in `~/.ssh/id_rsa`.

Next, a new pair of public/private keys is generated (mind the new key names in order not to overwrite the existing key). This new key pair will be the one used for subsequent communications between the master and the slave instances:
```bash
ssh-keygen -t rsa -P '' -f ~/.ssh/idhdfs_rsa
cat ~/.ssh/idhdfs_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
```

Once created, the new public key is uploaded to the slaves by means of `ssh-copy-id`. 
```bash
for x in cluster-slave-1 cluster-slave-2; do ssh-copy-id -i ~/.ssh/idhdfs_rsa.pub $x; done
```

Finally, the `lab` private key (`id_rsa`) is deleted, and the newly-created pair of keys is renamed so that the default key file names are used:
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

## Cluster instances configuration
Three configuration files have to be updated on master and slave instances in order to have the cluster configured: `core-site.xml`, `hdfs-site.xml`, and `slaves` (mind that some variables have been deprecated as new versions of Hadoop come out, be aware of that). They are available in the directory `$HADOOP_CONF_DIR`. Although there are some options that are only relevant for the master, it is simpler to copy the same configuration files to all the instances in the cluster.

### `core-site.xml`
First, `core-site.xml` must be updated on all instances (master and slaves), in order to set the properties `hadoop.tmp.dir` and `fs.defaultFS`:
```bash
nano $HADOOP_CONF_DIR/core-site.xml
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
nano $HADOOP_CONF_DIR/hdfs-site.xml
```
```xml
<configuration>
<property>
  <name>dfs.replication</name>
    <value>3</value>
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
</configuration>
```

Some remarks about the variables:
* `dfs.replication`: it specifies the default block replication. That is, it defines how many machines a single file should be replicated to before it becomes available. If its value is set to a value higher than the number of available slaves (actually *DataNodes*), there will errors. The default value is 3. As two slaves are available (plus an extra *DataNode* in the master instance), `dfs.replication` is set to 3.
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
cluster-slave-1
cluster-slave-2
" >> $HADOOP_CONF_DIR/slaves
```

## HDFS filesystem format via the *NameNode*
It can be done by means of the HDFS CLI (mind that if the filesystem is formatted again in some time in the future, there will be errors related to inconsistent clusterID; *DataNodes* on slave instances will keep the reference to the old *NameNode* and thus deletion and recreation of data folders will be needed):
```bash
$HADOOP_HOME/bin/hdfs namenode -format
```

## Distributed File System start
Although it is possible to start HDFS and YARN daemons at once, it is better to run tehem separately, obviously if YARN is not needed. The scripts for starting and stopping the HDFS and YARN daemons are available in the `$HADOOP_HOME/sbin` folder. HDSF daemons are started by running, only in the master node, the following script:
```bash
$HADOOP_HOME/sbin/start-dfs.sh
```

To validate it has started successfully, `jps` can be run on the master and slave instances. The output should list `NameNode`, `SecondaryNameNode`, and` DataNode` on the master node:
```bash
17089 DataNode
16947 NameNode
17324 SecondaryNameNode
17470 Jps
```

And a `DataNode` in each slave instance.

If this output is not got on all the instances of the cluster, it is necessary to analyze the log files available at `HADOOP_LOG_DIR`. Relevant log files are `hadoop-ubuntu-datanode-cluster-master.log`, `hadoop-ubuntu-namenode-cluster-master.log`, and `hadoop-ubuntu-secondarynamenode-cluster-master.log`.

The status of the HDFS cluster can be verified in `http://<master-floating-ip-address>:50070/`

To stop the HDFS cluster, simply type:
```bash
$HADOOP_HOME/sbin/stop-dfs.sh
```

## Key take-aways

Works such as *Spark in action* (Manning, 2017) state that "The installation [of YARN and Hadoop] is straightforward", but depending on the environment it can be not totally true. The main issues addressed when setting up the Hadoop cluster in the considered scenario (OpenStack cloud with Ubuntu 16.04 instances) are the following ones:
* private IP addresses must be used to refer to the cluster instances in the configuration files. If floating IP addresses are used, it will be not possible to connect any instance to each other (it is possible to override this behavior by setting the properties `*-bind-host` en `hdfs-site.xml` to 0.0.0.0, but this kind of configuration is not possible in Spark).
* password-less ssh is easy to implement provided that it is possible copy the public keys to all the slave instances. As an OpenStack cloud that follows exactly the same principle is used, uploading a suitable key to the slaves can be tricky. The second alternative described above (using a specific pair of keys for enabling cluster communication) is recommended as it exposes the cloud master key just for a while.

## See also
* [Deploying YARN on a Hadoop cluster](./yarn-cluster-setup.md)
* [Running Spark on a YARN cluster](./spark-yarn-cluster-setup.md)
* [Running Spark on a standalone cluster](./spark-standalone-cluster-setup.md)