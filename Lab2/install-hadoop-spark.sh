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
source ~/.profile

# install spark
sudo apt install python3-pip -y
pip install pyspark


