# Sparkling Water setup

1. Java installation in all cluster instances.
2. /etc/host upldate in all cluster instances.
3. Password-less ssh configuration
4. Spark installation in all cluster instances.
5. Creation of slaves file in the master instance.
6. Installation and configuration of Anaconda (Python 3.5)
7. H2O Installation
8. Sparkling Water Installation

--------

Our environment is made of two instances, one master and one slave. Master is named `tb012`, with IP address 192.168.0.12. First slave is named `tb013`, with IP address 192.168.0.13.

## /etc/hosts update in all instances
The instances must be able to connect to each other. Thus, we add the following lines to the `/etc/hosts` file in each instance:

```bash
echo "
192.168.0.12		cluster-master
192.168.0.13	cluster-slave-1
" | sudo tee --append /etc/hosts
```

## Spark installation on all instances
A Spark release compatible with Hadoop 2.7.4 and Zeppelin 0.7.2, [Spark 2.0.2](https://spark.apache.org/releases/spark-release-2-0-2.html), is chosen. Use a symbolic link to easily upgrade or change versions if wished.

```bash
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.0.2-bin-hadoop2.7.tgz
tar -zxvf spark-2.0.2-bin-hadoop2.7.tgz
sudo mkdir -p /opt/sparks
sudo mv spark-2.0.2-bin-hadoop2.7 /opt/sparks
sudo ln -s /opt/sparks/spark-2.0.2-bin-hadoop2.7 /usr/local/spark
rm spark-2.0.2-bin-hadoop2.7.tgz
```

### Spark environment variables setup on master and slave nodes
The following environment variables are set in the `.bashrc` file under `/home/ecemaml` (both on master and slave nodes):
```bash
echo '
# Set SPARK_HOME
export SPARK_HOME=/usr/local/spark
# Add Spark bin and sbin directories to PATH
export PATH=$PATH:$SPARK_HOME/sbin:$SPARK_HOME/bin
' >> ~/.bashrc
```

The `.bashrc` file is reloaded:
```bash
source ~/.bashrc
```

### Additional Spark configuration
Next, some additional variables in the `spark-env.sh` configuration file are activated and set on the master node:
```bash
cp $SPARK_CONF_DIR/spark-env.sh.template $SPARK_CONF_DIR/spark-env.sh
echo '
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export SPARK_MASTER_HOST=192.168.0.12
export SPARK_LOCAL_IP=192.168.0.12
' >> $SPARK_CONF_DIR/spark-env.sh
```

A simila update is done in the slave nodes (see example for existing slave):

```bash
cp $SPARK_CONF_DIR/spark-env.sh.template $SPARK_CONF_DIR/spark-env.sh
echo '
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export SPARK_MASTER_HOST=192.168.0.12
export SPARK_LOCAL_IP=192.168.0.13
' >> $SPARK_CONF_DIR/spark-env.sh
```

It is possible to determine whether the installation has been right by running the `spark-shell` command in any instance (`spark-shell` without arguments is equivalent to `spark-shell --master local[*]`). Besides some warnings, the output should be something like this (to exit the Spark shell, type CTRL-D) when run on the master instance:
```bash
Spark context Web UI available at http://<master-ip-address>:4040
Spark context available as 'sc' (master = local[*], app id = local-1503914008988).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ \`/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.0.2
      /_/

Using Scala version 2.11.8 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_144)
Type in expressions to have them evaluated.
Type :help for more information.
```
If you try to run `pyspark`, an error will be raised  (sort of "Python not found" error), as python has not been installed yet.

Before leaving the shell, it is possible to verify the status of the Spark context created by running the shell in `http://<master-floating-ip-address>:4040/`:

![Spark Context UI](./images/spark-context-shell-idle.PNG)

### Spark cluster slaves configuration
The Spark `slaves` file must be created, only on the master node.
```bash
echo "cluster-slave-1
" > $SPARK_CONF_DIR/slaves
```

### Cluster start and stop
In the master:
```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slaves.sh 
``` 
Instead, it is possible start *Master* and *Workers* at the same time:
```bash
$SPARK_HOME/sbin/start-all.sh 
``` 

To validate the cluster has been successfully started, the JVM Process Status tool can be run on the master and slave instances. The output should list `Worker` and `Master` on the master node:
```bash
11512 Worker
10920 Master
11677 Jps
```

And a `Worker` process in each slave instance.

The status of the Spark cluster can be verified in `http://<master-floating-ip-address>:8080/`:

![Spark Standalone Cluster UI](./images/spark-standalone-idle.PNG)

Only one worker must appear. No applications (running or completed) are listed and no Spark context UI is available.

To terminate the cluster, you can stop *Master* and *Workers* separately or just with a single command:
```bash
$SPARK_HOME/sbin/stop-master.sh
$SPARK_HOME/sbin/stop-slaves.sh 
``` 
Or:
```bash
$SPARK_HOME/sbin/stop-all.sh 
``` 

When the cluster is stopped, the Spark Cluster UI becomes unreachable.

Next, it is possible to verify whether `spark-shell` run against the cluster. First, the cluster is started again (both master and slaves). Next, the `spark-shell` is run with the `master` argument set to the IP address of the Spark Standalone cluster:
```bash
spark-shell --master spark://<master-ip-address>:7077
```
Besides some warnings, the output should is something such as this:

```bash
Spark context Web UI available at http://<master-ip-address>:4040
Spark context available as 'sc' (master = spark://<master-ip-address>:7077, app id = app-20170828131641-0000).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ \`/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.0.2
      /_/

Using Scala version 2.11.8 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_144)
Type in expressions to have them evaluated.
Type :help for more information.
```

If we verify the status of the Spark cluster (in `http://<master-floating-ip-address>:8080/`):

![Spark Standalone Cluster UI](./images/spark-standalone-shell.PNG)

We find the existing *Worker* listed in the previous screenshot **and** the Spark shell as a new *Running Application*. At the same time, the Spark context UI (`http://<master-floating-ip-address>:4040/`) is available as well.

## Python Installation and Configuration
Python is handled by means of an [Anaconda Distribution](https://www.anaconda.com/distribution/), which is installed on master and slave instances. The release is 4.2.0. It includes not only Python 3.5 but a number of valuable Python packages and Jupyter Notebook as well (a **note about versions**: From 4.4, the Anaconda Distribution is based on Python 3.6; however, Spark 2.0 does not support Python 3.6, so that an earlier version of the Anaconda Distribution is required):

```bash
wget https://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh
sudo /bin/bash Anaconda3-4.2.0-Linux-x86_64.sh -b -p /usr/local/anaconda
sudo chown -R ecemaml:ecemaml /usr/local/anaconda/
rm Anaconda3-4.2.0-Linux-x86_64.sh
sudo /usr/local/anaconda/bin/conda update -y conda
```

Next, the following environment variables must are set in the `.bashrc` file under `/home/ecemaml` (both on master and slave nodes):
```bash
echo '
# Set ANACONDA_HOME
export ANACONDA_HOME=/usr/local/anaconda
# Add Anaconda bin directory to PATH
export PATH=$ANACONDA_HOME/bin:$PATH' >> ~/.bashrc
```

Finally, the `.bashrc` file is reloaded:
```bash
source ~/.bashrc
```
## Jupyter Notebook configuration
Jupyter can be used to run Pyspark applications as notebooks. However, for the Notebook server to be accessible from sites other than the localhost, some configuration is needed. First, a configuration file for Jupyter Notebook must be created on the master instance (the file is needed for enabling access to the Notebook server):

```bash
/usr/local/anaconda/bin/jupyter notebook --generate-config -y
```

As a result, `~/.jupyter/jupyter_notebook_config.py` is created. Some setting in the configuration file must be updated as well in order to:
* Know which folder for notebooks and kernels must use.
* Enable access to the Notebook server from clients other than `localhost`. By default the Notebook server only listens on the `localhost` network interface. To enable connection from any client, the Notebook server must listen on all network interfaces and not open the browser.
* Tune the security settings. Security in the Jupyter Notebook server is enabled by requesting an authentication token, created when Jupyter is run from the command line. As access to the command line is not always possible, two different options can be taken:
  1. Enabling a password. This is the preferred option.
  2. Disabling the authentication. This option is discouraged.

### Notebooks folder
The folder that hosts notebooks and kernels is created and proper permissions assigned:
```bash
sudo mkdir /srv/notebooks
sudo chown ecemaml:ecemaml ./notebooks/
```

Next, the Jupyter Notebook configuration file, `~/.jupyter/jupyter_notebook_config.py`, is updated to use the just created folder, by activating the `c.NotebookApp.notebook_dir` setting:
```bash
sed -i "s/#c.NotebookApp.notebook_dir = ''/c.NotebookApp.notebook_dir = '\/srv\/notebooks'/" ~/.jupyter/jupyter_notebook_config.py
```

### Noteboook Server access
For making the server accessible from any client, the following settings must be activated and/or modified: `c.NotebookApp.ip`, and `c.NotebookApp.open_browser` (see [Running a public Notebook server](http://jupyter-notebook.readthedocs.io/en/latest/public_server.html#running-a-public-notebook-server)). It allows to access the server from clients other than the `localhost` and not to start the browser when `jupyter notebook` is run:
```bash
sed -i "s/#c.NotebookApp.ip = 'localhost'/c.NotebookApp.ip = '*'/" ~/.jupyter/jupyter_notebook_config.py
sed -i "s/#c.NotebookApp.open_browser = True/c.NotebookApp.open_browser = False/" ~/.jupyter/jupyter_notebook_config.py
```
The Jupyter Notebook server can be accessed in `http://<master-ip-address>:8888/`:

Finally, some considerantions about the security. The configuration above enables a public Notebook server. Security is enabled by requesting an authentication token, created when Jupyter is run from the command line. Two options are considered

#### Disabling token authentication (discouraged)
```bash
sed -i "s/#c.NotebookApp.token = '<generated>'/c.NotebookApp.token = ''/" ~/.jupyter/jupyter_notebook_config.py
```

#### Enabling password authentication
If using `my_password` as password:
```bash
sed -i "s/#c.NotebookApp.password = ''/c.NotebookApp.password = 'my_password'/" ~/.jupyter/jupyter_notebook_config.py
```

## Sparkling Water Installation
The description below is based on [official documentation](http://h2o-release.s3.amazonaws.com/sparkling-water/rel-2.0/2/index.html) and on a [My Big Data World blog post](https://weidongzhou.wordpress.com/2017/11/06/h2o-vs-sparkling-water/). 

As the Sparkling Water release is aligned with the Spark release, use Sparkling Water 2.0. Download the package and install it in the cluster manager (we're using a symbolic link to enable version upgrade):
 
```bash
wget http://h2o-release.s3.amazonaws.com/sparkling-water/rel-2.0/22/sparkling-water-2.0.22.zip
sudo mkdir -p /opt/sparkling-waters
sudo unzip sparkling-water-2.0.22.zip -d /opt/sparkling-waters
sudo ln -s /opt/sparkling-waters/sparkling-water-2.0.22 /usr/local/sparkling-water
rm sparkling-water-2.0.22.zip
```

The following environment variables are set in the `.bashrc` file under `/home/ecemaml`:
```bash
echo '
# Set SPARKLING_HOME
export SPARK_HOME=/usr/local/sparkling-water
# Add Sparkling Water bin directory to PATH
export PATH=$PATH:$SPARKLING_HOME/sbin' >> ~/.bashrc
```

Finally, the `.bashrc` file is reloaded:
```bash
source ~/.bashrc
```

It is possible to verify the right installation of Sparkling Water by running the shell (`sparkling-shell` accepts the same arguments as the regular Spark shell):
```bash
sparkling-shell --master spark://<master-ip-address>:7077 \
--conf spark.executor.instances=2 \
--conf spark.executor.memory=2g \
--conf spark.driver.memory=2g \
--conf spark.sql.autoBroadcastJoinThreshold=-1 \
--conf spark.locality.wait=30000 \
--conf spark.scheduler.minRegisteredResourcesRatio=1
```

The output should be something like this (to exit the  shell, type CTRL-D) when run on the master instance:

```bash

-----
  Spark master (MASTER)     : spark://<master-ip-address>:7077
  Spark home   (SPARK_HOME) : /usr/local/spark
  H2O build version         : 3.16.0.4 (wheeler)
  Spark build version       : 2.0.2
  Scala version             : 2.11
----

Java HotSpot(TM) 64-Bit Server VM warning: ignoring option MaxPermSize=384m; support was removed in 8.0
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel).
Spark context Web UI available at http://<master-ip-address>:4040
Spark context available as 'sc' (master = spark://<master-ip-address>:7077, app id = app-20180202113529-0002).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.0.2
      /_/

Using Scala version 2.11.8 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_161)
Type in expressions to have them evaluated.
Type :help for more information.
```

## Pysparkling installation
The description is based on [official documentation](https://github.com/h2oai/sparkling-water/blob/rel-2.0/py/README.rst) and on a [My Big Data World blog post](https://weidongzhou.wordpress.com/2017/11/06/h2o-vs-sparkling-water/). 

In order to use the `pysparkling`, you must install the H2O dependencies: 

```bash
sudo /usr/local/anaconda/bin/conda install -y -c anaconda requests 
sudo /usr/local/anaconda/bin/conda install -y -c conda-forge tabulate 
sudo /usr/local/anaconda/bin/conda install -y -c conda-forge colorama
sudo /usr/local/anaconda/bin/conda install -y -c conda-forge future
```

Finally, install `pysparkling` in the master instance in the cluster:
```bash
sudo pip install h2o_pysparkling_2.0
```

It is possible to verify the right installation of pysparkling by running it (`sparkling-shell` accepts the same arguments as the regular Spark shell):
```bash
pysparkling --master spark://<master-ip-address>:7077 \
--conf spark.executor.instances=2 \
--conf spark.executor.memory=2g \
--conf spark.driver.memory=2g \
--conf spark.sql.autoBroadcastJoinThreshold=-1 \
--conf spark.locality.wait=30000 \
--conf spark.scheduler.minRegisteredResourcesRatio=1
```

Next, you 

![Project infrastructure](./images/h2o-flow.PNG)
