#!/bin/sh

wget --progress=bar:force:noscroll https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz
echo "Unpacking..."
tar -xf hadoop-3.3.4.tar.gz
sudo mv hadoop-3.3.4 /usr/local/
sudo apt-get update && sudo apt-get install -y openjdk-8-jre-headless openjdk-8-jdk-headless unzip
echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/" >> ~/.profile
echo "export PATH=$JAVA_HOME/bin:$PATH" >> ~/.profile
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> ~/.profile
echo "export PATH=/usr/local/hadoop-3.3.4/bin:$PATH" >> ~/.profile
echo "export PATH=$HADOOP_HOME/bin:$PATH" >> ~/.profile
echo "export PATH=/usr/local/spark/bin:$PATH" >> ~/.profile
echo "export SPARK_HOME=/usr/local/spark" >> ~/.profile
source ~/.profile

# install spark
wget https://archive.apache.org/dist/spark/spark-2.0.0/spark-2.0.0-bin-hadoop2.7.tgz
tar -xzf spark-2.0.0-bin-hadoop2.7.tgz
mv spark-2.0.0-bin-hadoop2.7 spark
# sudo apt install python3-pip -y
# pip install pyspark


