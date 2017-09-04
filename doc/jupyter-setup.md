# Running Jupyter notebooks on a Spark Standalone cluster
[Jupyter Notebook](https://jupyter.org/) is a web-based application initially created for the Python language (but supporting right now many others) that allows creating *notebooks documents* by means of a web browser and executing it by means of a *kernel*. Jupyter Notebooks are ideal means for running `pyspark` applications and therefore will be one of the main choices when carrying out projects like this. The instance where Jupyter is running needn't be the master node or even one of the cluster instances. However, exactly the same Python and Jupyter versions have to be used in both the node where Jupyter is running and the cluster instances.

* [Python installation](#python-installation)
* [Jupyter Notebook configuration](#jupyter-notebook-configuration)
* [Jupyter Notebook execution](#jupyter-notebook-execution)
* [See also](#see-also)

----

## Python installation
An Anaconda Python distribution is installed on master and slave instances. It installs not only Python 2.7 but a number of valuable Python packages and Jupyter Notebook as well:

```bash
wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh
sudo /bin/bash Anaconda2-4.2.0-Linux-x86_64.sh -b -p /usr/local/anaconda
sudo chown -R ubuntu:ubuntu /usr/local/anaconda/
rm Anaconda2-4.2.0-Linux-x86_64.sh
/usr/local/anaconda/bin/conda update -y conda
```
Additionally, although not actually needed in the chosen configuration, [`findspark`](https://github.com/minrk/findspark) is installed (`findspark` is a Python module that allows to call `pyspark` from Python scripts; as we plan to trigger notebook execution by running the `pyspark` command, it is not actually needed).

```bash
/usr/local/anaconda/bin/conda install -c conda-forge findspark -y
```
Finally, a configuration file for Jupyter Notebook is created (the file is needed for enabling access to the notebook server, see [Jupyter Notebook execution](#jupyter-notebook-execution)):

```bash
/usr/local/anaconda/bin/jupyter notebook --generate-config -y
```

As a result, `~/.jupyter/jupyter_notebook_config.py` is created.

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

Verification of a right Python 2.7 installation can be done by typing `python`. The output should be similar to this:
```bash
Python 2.7.12 |Anaconda custom (64-bit)| (default, Jul  2 2016, 17:42:40)
[GCC 4.4.7 20120313 (Red Hat 4.4.7-1)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
Anaconda is brought to you by Continuum Analytics.
Please check out: http://continuum.io/thanks and https://anaconda.org
>>>
```

Next, verification of `pyspark` availability is carried out. The output should be similar to this:
```bash
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ \`/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 2.0.2
      /_/

Using Python version 2.7.12 (default, Jul  2 2016 17:42:40)
SparkSession available as 'spark'.
```

Finally, a similar verification, but against the Spark Standalone cluster, can be done:
```bash
pyspark --master spark://<master-floating-ip-address>:7077
```

## Jupyter Notebook configuration
The default Jupyter Notebook configuration must be updated in order to:
* Know which folder for notebooks and kernels must be used.
* Enable access to the Notebook server in hosts other than `localhost`. By default the Notebook server only listens on the `localhost` network interface. To enable connection from other clients, the Notebook server to listen on all network interfaces and not open the browser.
* Define the port the Notebook server should listen to. A known, fixed port is set: 9999.

The folder that hosts notebooks and kernels is created:
```bash
mkdir ~/notebooks
```

Next, the Jupyter Notebook configuration file, `~/.jupyter/jupyter_notebook_config.py`, is be updated to use the just created folder and for enable the access from external IP addresses to the notebooks. Four properties are activated and set: `c.NotebookApp.notebook_dir`, `c.NotebookApp.ip`, `c.NotebookApp.open_browser`, and `c.NotebookApp.port`:
```bash
sed -i "s/#c.NotebookApp.notebook_dir = u''/c.NotebookApp.notebook_dir = u'\/home\/ubuntu\/notebooks'/" ~/.jupyter/jupyter_notebook_config.py
sed -i "s/#c.NotebookApp.ip = 'localhost'/c.NotebookApp.ip = '*'/" ~/.jupyter/jupyter_notebook_config.py
sed -i "s/#c.NotebookApp.open_browser = True/c.NotebookApp.open_browser = False/" ~/.jupyter/jupyter_notebook_config.py
sed -i "s/#c.NotebookApp.port = 8888/c.NotebookApp.port = 9999/" ~/.jupyter/jupyter_notebook_config.py
```
The configuration above enables a public Notebook server. There is no built-in security and that is acceptable as a private Openstack cloud is being used. In open environments, the server must be secured with a password and TLS (see [Running a public notebook server](http://jupyter-notebook.readthedocs.io/en/latest/public_server.html#running-a-public-notebook-server)).

Finally, Spark must be configured to run a notebook when `pyspark` is invoked.

```bash
echo '
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS="notebook"
' >> $SPARK_CONF_DIR/spark-env.sh
```
Mind that there are other ways to run notebooks when `pyspark` is involved and enabling access from external IP addresses to the Notebook server. Provided that only `c.NotebookApp.notebook_dir` is activated in `~/.jupyter/jupyter_notebook_config.py` the remaining Jupyter configuration properties can be set in `$SPARK_CONF_DIR/spark-env.sh`:
```bash
echo '
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS="notebook --port=9999 --no-browser --ip=*"
' >> $SPARK_CONF_DIR/spark-env.sh
```

## Jupyter Notebook execution
The execution of Jupyter Notebook is triggered when `pyspark` is run: an output similar to this is printed in the console:

```bash
[I 15:44:57.323 NotebookApp] [nb_conda_kernels] enabled, 2 kernels found
[I 15:44:57.337 NotebookApp] Writing notebook server cookie secret to /run/user/1000/jupyter/notebook_cookie_secret
[W 15:44:57.380 NotebookApp] WARNING: The notebook server is listening on all IP addresses and not using encryption. This is not recommended.
[W 15:44:57.381 NotebookApp] WARNING: The notebook server is listening on all IP addresses and not using authentication. This is highly insecure and not recommended.
[I 15:44:57.553 NotebookApp] V nbpresent HTML export ENABLED
[W 15:44:57.554 NotebookApp] X nbpresent PDF export DISABLED: No module named nbbrowserpdf.exporters.pdf
[I 15:44:57.562 NotebookApp] [nb_conda] enabled
[I 15:44:57.722 NotebookApp] [nb_anacondacloud] enabled
[I 15:44:57.738 NotebookApp] Serving notebooks from local directory: /home/ubuntu/notebooks
[I 15:44:57.738 NotebookApp] 0 active kernels
[I 15:44:57.738 NotebookApp] The Jupyter Notebook is running at: http://[all ip addresses on your system]:9999/
[I 15:44:57.738 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
```

At the same the Jupyter Notebook server is accessible in `http://<master-floating-ip-address>:9999/`:

![Spark Notebook](./spark-notebook-empty.PNG)

Once the *kernel* is loaded, it is possible to start to create and execute notebooks. The Jupyter Notebook server can be terminated by typing CTRL-C.

Next, the Jupyter Notebook server can be run against the Spark cluster. First, the cluster must be started. Next, the appropriate master is chosen:
```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-slaves.sh 
pyspark --master spark://<master-ip-address>:7077
```

## See also
* [Running Zeppelin notebooks on a Spark Standalone cluster](./zeppelin-setup.md)
