#!/usr/bin/env bash
sudo mkdir text_files
cd text_files
wget https://tinyurl.com/4vxdw3pa
wget https://tinyurl.com/kh9excea
wget https://tinyurl.com/dybs9bnk
wget https://tinyurl.com/datumz6m
wget https://tinyurl.com/j4j4xdw6
wget https://tinyurl.com/ym8s5fm4
wget https://tinyurl.com/2h6a75nk
wget https://tinyurl.com/vwvram8
wget https://tinyurl.com/weh83uyn
cd ..
hdfs dfs -mkdir input
hdfs dfs -copyFromLocal text_files/* input
time hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-map/reduce-examples-3.3.4.jar wordcount input output