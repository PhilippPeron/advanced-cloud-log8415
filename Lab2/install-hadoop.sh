#!/bin/sh

wget --progress=bar:force:noscroll https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz
echo "Unpacking..."
tar -xf hadoop-3.3.4.tar.gz
sudo mv hadoop-3.3.4 /usr/local/
sudo apt-get update && sudo apt-get install -y openjdk-11-jre-headless openjdk-11-jdk-headless unzip
echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/" >> ~/.profile 
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> ~/.profile 
echo "export PATH=/usr/local/hadoop-3.3.4/bin:$PATH" >> ~/.profile

