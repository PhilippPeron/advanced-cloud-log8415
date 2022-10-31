#!/bin/sh

wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz
tar -xf hadoop-3.3.4.tar.gz
sudo mv hadoop-3.3.4 /usr/local/
sudo apt update -y && sudo apt install -y openjdk-11-jre-headless
echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/" >> ~/.profile 
echo "export HADOOP_PREFIX=/usr/local/hadoop-3.3.4" >> ~/.profile 
echo "export PATH=/usr/local/hadoop-3.3.4/bin:$PATH" >> ~/.profile

