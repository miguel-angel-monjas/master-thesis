# Data load
## Data size
The dataset to analyze is made of six files recording each one month call detail records. Once uncompressed (one of them is corrupted and only part of the file has been recovered), their size is:

```bash
-rw-rw-r--  1 ubuntu ubuntu 42473368189 Mar  5  2016 DWFET_CDR_CELLID_201510.csv
-rw-rw-r--  1 ubuntu ubuntu 42319207977 Mar  5  2016 DWFET_CDR_CELLID_201511.csv
-rw-rw-r--  1 ubuntu ubuntu 52670621324 Mar  5  2016 DWFET_CDR_CELLID_201512.csv
-rw-rw-r--  1 ubuntu ubuntu 52279262820 Mar  5  2016 DWFET_CDR_CELLID_201601.csv
-rw-rw-r--  1 ubuntu ubuntu 30836942213 Mar  5  2016 DWFET_CDR_CELLID_201602.csv
-rw-rw-r--  1 ubuntu ubuntu   Mar  5  2016 DWFET_CDR_CELLID_201603.csv
```

## Data upload to HDFS
Once the HDFS cluster is running, data can be uploaded to it by using the [HDFS File System (FS) shell](https://hadoop.apache.org/docs/r2.7.4/hadoop-project-dist/hadoop-common/FileSystemShell.html). First, the file is uploaded to the master node and next put in the HDFS cluster. For instance, once a file (`DWFET_CDR_CELLID_201512.csv`) has been uploaded to the master node, it is stored in HDFS:
```bash
hdfs dfs -mkdir /data
hdfs dfs -put DWFET_CDR_CELLID_201612.csv /data
```

In order to verify that the file has been loaded, the HDFS Web Interface (`http://<master-floating-ip-address>:50070/` > Utilities > Browse the file system) can be accessed:

![Hadoop Web Interface: uploaded file](./hadoop-single-file.PNG)

## Data upload to HDFS as parquet files

A similar procedure will be executed for every file the dataset is made of. Next, Spark will be used to retrieve data files from the HDFS cluster and save the content as parquet files. Next, the original files will be deleted, as they are no longer valid:
```bash
hdfs dfs -rm /data/DWFET_CDR_CELLID_201602.csv
hdfs dfs -expunge
```