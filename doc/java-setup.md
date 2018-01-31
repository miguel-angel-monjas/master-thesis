# Java Installation in the cluster nodes
All the components of the HDFS/Spark cluster are based on the JVM and therefore, Java must be installed in all of them before starting the installation of Hadoop, Spark and any other additional component.

* [Java installation on all instances](#java-installation-on-all-instances)
* [Environment variables setup on all instances](#environment-variables-setup-on-all-instances)
* [See also](#see-also)

-----

## Java installation on all instances
Java must be installed in all the cluster instances: ***Oracle Java 8*** has been chosen (some tutorials found on the Internet, such as [this](http://tecadmin.net/install-oracle-java-8-jdk-8-ubuntu-via-ppa/) and [this](http://stackoverflow.com/questions/19275856/auto-yes-to-the-license-agreement-on-sudo-apt-get-y-install-oracle-java7-instal)) are used):

```bash
sudo apt-get update
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get install -y oracle-java8-installer
sudo apt-get install -y oracle-java8-set-default
```

Verification of a successful Java installacion can be done by typing `java -version` in the console. The output must be similar to this:
```bash
java version "1.8.0_144"
Java(TM) SE Runtime Environment (build 1.8.0_144-b01)
Java HotSpot(TM) 64-Bit Server VM (build 25.144-b01, mixed mode)
```

## Environment variables setup on all instances
In order to determine the actual Java home, the following command can be used:
```bash
readlink -f /usr/bin/java | sed "s:bin/java::"
```

Next, the following environment variable must set in the `.bashrc` file under `/home/ubuntu` (on all the instances):
```bash
echo '
# Set JAVA_HOME 
export JAVA_HOME=/usr/lib/jvm/java-8-oracle/jre
' >> ~/.bashrc
```

Once updated, the `.bashrc` file must be reloaded:
```bash
source ~/.bashrc
```

## See also
* [Infrastructure deployment index](./infrastructure.md)
* [Setting up an HDFS cluster](./hadoop-cluster-setup.md).
* [Setting up and running a Standalone Spark cluster](./spark-standalone-cluster-setup.md).