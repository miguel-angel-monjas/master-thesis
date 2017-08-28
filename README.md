# "A real case: Spark-assisted analysis of telecom operator Call Detail Records (CDR)"
### [Master in Data Science](http://www.masterdatascience.es/)'s Thesis, by **Miguel-Angel Monjas**

This thesis documents the whole process that has taken out in order to implement a simple analytics project. This project aimed to make sense of a large dataset which contained several months Call Detail Records (CDR) of a telecom operator, Operator X. Operator X serves a small country in Europe and is mainly interested in knowing about the incoming roamers (i.e. subscribers from abroad served by Operator X when they are in the territory served by Operator X). The process this thesis documents goes through the actual knowledge extraction but also infrastructure deployment on an OpenStack cluster.

## Infrastructure deployment
The following guidelines have been generated:
* [Setting up a Hadoop cluster](doc/hadoop-cluster-setup.md)
* [Deploying YARN on a Hadoop cluster](doc/yarn-cluster-setup.md)
* [Running Spark on a YARN cluster](doc/spark-yarn-cluster-setup.md)
* [Running Spark on a standalone cluster](doc/spark-standalone-cluster-setup.md)