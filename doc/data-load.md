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

## Dataset upload to HDFS
Once the HDFS cluster is running, data can be uploaded to it by using the [HDFS File System (FS) shell](https://hadoop.apache.org/docs/r2.7.4/hadoop-project-dist/hadoop-common/FileSystemShell.html). First, the file is uploaded to the master node and next put in the HDFS cluster. For instance, once a file (`DWFET_CDR_CELLID_201512.csv`) has been uploaded to the master node, it is stored in HDFS:
```bash
hdfs dfs -mkdir /data
hdfs dfs -put DWFET_CDR_CELLID_201612.csv /data
```

In order to verify that the file has been loaded, the HDFS Web Interface (`http://<master-floating-ip-address>:50070/` > Utilities > Browse the file system) can be accessed:

![Hadoop Web Interface: uploaded file](./hadoop-single-file.PNG)

The same procedure will be executed for every file the dataset is made of.

## Data upload to HDFS as parquet files
Next, Spark will be used to retrieve data files from the HDFS cluster and save their contents as parquet files:
```python
from pyspark.sql.types import StructType, StructField, ArrayType, BooleanType, IntegerType, StringType, TimestampType

customSchema = StructType([StructField("DS_CDMSISDN", StringType(), True),
                            StructField("DS_CDIMSI", StringType(), True),
                            StructField("DS_IMEI", StringType(), True),
                            StructField("DT_CDDATASTART", TimestampType(), True),
                            StructField("DT_CDDATAEND", TimestampType(), True),
                            StructField("6NUM_LENGTH", StringType(), True),
                            StructField("ID_CELL_START", StringType(), True),
                            StructField("ID_CELL_END", StringType(), True),
                            StructField("DS_CALLIDENTIFICATIONNUMBER", StringType(), True),
                            StructField("ID_RECORDSEQUENCENUMBER", StringType(), True),
                            StructField("ID_CDTIPUSCOM", StringType(), True),
                            StructField("DS_CDCENTRAL", StringType(), True),
                            StructField("ACTUALIZACION_DATE", StringType(), True),
                            StructField("ID_CLIENTSOURCE", StringType(), True),
                            StructField("ID_CDOPERATORSOURCE", StringType(), True),
                            StructField("ID_CDCOUNTRYSOURCE", StringType(), True),
                            StructField("DS_CDNUMDEST", StringType(), True),
                            StructField("ID_CDOPERATORDESTI", StringType(), True),
                            StructField("TAC_IMEI", StringType(), True),
                          ])
						  
input_file = u'hdfs://cluster-master:9000/data/DWFET_CDR_CELLID_201612.csv'
df = spark.read.format('csv').\
                            load(input_file,
                                sep=';',
                                header=True,
                                schema = customSchema,
                                timestampFormat = 'yyyy.MM.dd hh:mm:ss'
                            ).\
                            drop("DS_CDIMSI").\
                            drop("ID_RECORDSEQUENCENUMBER").\
                            drop("DS_CDCENTRAL").\
                            drop("ACTUALIZACION_DATE")
							
output_file = u'hdfs://cluster-master:9000/data/DWFET_CDR_CELLID_201612.parquet'
df.write.parquet(output_file)
```

![Hadoop Web Interface: parquet file](./hadoop-single-parquet-file.PNG)


Next, the original files will be deleted, as they are no longer valid:
```bash
hdfs dfs -rm /data/DWFET_CDR_CELLID_201602.csv
hdfs dfs -expunge
```

## Auxiliary data upload to HDFS
A similar procedure will be carried out in order to store auxiliary data (`TAC.csv` and `MCCMNC.csv`) in the HDFS cluster. Once uploaded to the master node, the following commands are run:
```bash
hdfs dfs -put TAC.csv /data
hdfs dfs -put MCCMNC.csv /data
```