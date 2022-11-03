#!/usr/bin/env bash

LOG_FILE='word_count.time'

sudo mkdir text_files
cd text_files
# Download files
sudo wget https://tinyurl.com/4vxdw3pa
sudo wget https://tinyurl.com/kh9excea
sudo wget https://tinyurl.com/dybs9bnk
sudo wget https://tinyurl.com/datumz6m
sudo wget https://tinyurl.com/j4j4xdw6
sudo wget https://tinyurl.com/ym8s5fm4
sudo wget https://tinyurl.com/2h6a75nk
sudo wget https://tinyurl.com/vwvram8
sudo wget https://tinyurl.com/weh83uyn
cd ..
# Create hdfs folder
hdfs dfs -mkdir input

# Retrieve wordcount.py path
WORD_COUNT_PYSPARK=`sudo find / -name wordcount.py`
# Copy files into hadoop file system and process input files in text_files directory
for FILE in `ls text_files/*-00-* | cut -d"/" -f2`
do
  hdfs dfs -copyFromLocal "text_files/$FILE" input
  echo  >>LOG_FILE
  echo "$FILE" >>LOG_FILE
  echo 'Spark:' >>LOG_FILE
  # Run spark command
  { time python3 "$WORD_COUNT_PYSPARK" "text_files/$FILE"; } 2>&1 | tail -n3 >>LOG_FILE
  echo 'Hadoop:' >>LOG_FILE
  # Run hadoop command
  { time hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-map/reduce-examples-3.3.4.jar wordcount "input/$FILE" output; } 2>&1 | tail -n3 >>LOG_FILE
  echo "" >>LOG_FILE
  # Cleanup output folder
  hdfs dfs -rm -r output
done

# Cleanup input folder
hdfs dfs -rm -r input
op jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-map/reduce-examples-3.3.4.jar wordcount input output