# Environment description
The project aim to analyze a large amount of data (about 300 GB with about 55 million records) and therefore will require the set up of an HDFS cluster (to handle storage) and a Spark cluster, for processing. Additionally, there will be dedicated instances for visualization (a node hosting an [ELK Stack](https://www.elastic.co/webinars/introduction-elk-stack)) and for running the clients (clients will be based on notebooks): Jupyter and Zeppelin.

* [Instance creation](#instance-creation)
* [See also](#see-also)

----

## Instance creation
The project will rely on a private [Openstack](https://www.openstack.org/) cloud. The main reason not to use a public cloud provider lies in the confidential nature of the data to be analyzed. For privacy reasons it is not possible to transfer the data to other entities and therefore, in-house means have to be used.

The project will create the following instances:
* [Four instances for the HDFS/Spark cluster](#cluster-instances): one master and three slaves. The master instance will host only "master" processes: the HDFS cluster *NameNode* and the Spark cluster *Master* (no *Worker* or *DateNodes*).
* [One instance for hosting an ELK Stack](#client-instances).
* [One instance for hosting the notebook servers](#elk-stack-instance).

As with any other cloud-based solution, instances in Openstack are assigned an authentication key on creation so that no need to provide credentials at login is needed. Instead, ssh-based login by means of a private key available at the client is enabled. These keys are assigned to the user `ubuntu`. This default user has `sudo` privileges as well.

### HDFS/Spark Cluster instances
Four instances will be created, with the following hostnames `cluster-master`, `cluster-slave-1`, `cluster-slave-2` and `cluster-slave-3`. The OS used is Ubuntu 16.04 and the flavor (`spark-data-intensive`) has the following features:
* **Memory**: 32 GB
* **vCPU**: 16

All of them are given a private IP address, `<master-ip-address>`, `<slave-1-ip-address>`, `<slave-2-ip-address>` and `<slave-3-ip-address>`. A floating IP address must be manually assigned to the instances: `<master-floating-ip-address>` (slave instances are also assigned floating ip addresses, as it eases debugging; otherwise, access would be only possible through the master instance, by means of ssh connections).

### Client instances

### ELK Stack instance
A single instance will be created, with the following hostname: `elk`. The OS used is a Ubuntu 16:04 and the flavor (`data-intensive`) provides the following features:
* **Memory**: 16 GB
* **vCPU**: 4

It is given a private IP address: `<elk-ip-address>` and also a flotating IP address, `<elk-floating-ip-address>`. Otherwise, it will not be possible to access Kibana to visualize the information stored in Elasticsearch.

## See also
* [Setting up a Hadoop cluster](./hadoop-cluster-setup.md).
* [Running a Standalone Spark cluster](./spark-standalone-cluster-setup.md).
* [Deploying YARN on a Hadoop cluster](./yarn-cluster-setup.md).
* [Running a Spark cluster on YARN](./spark-yarn-cluster-setup.md).
