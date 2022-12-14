#!/usr/bin/env bash

LOG_FILE='word_count.time'
touch benchmark_results.txt

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
/usr/local/hadoop-3.3.4/bin/hdfs dfs -mkdir input

# Retrieve wordcount.py path
WORD_COUNT_PYSPARK=$(sudo find / -xdev -name wordcount.py)

# repeat three times to obtain an average
for i in 1 2 3
do
# Copy files into hadoop file system and process input files in text_files directory
  for FILE in `ls text_files/* | cut -d"/" -f2`
  do
    /usr/local/hadoop-3.3.4/bin/hdfs dfs -mkdir output
    /usr/local/hadoop-3.3.4/bin/hdfs dfs -copyFromLocal "text_files/$FILE" input
    echo "$FILE" >>benchmark_results.txt
    echo "Spark" >>benchmark_results.txt
    # Run spark command
    { /usr/bin/time -q -f "%e" python3 "$WORD_COUNT_PYSPARK" "text_files/$FILE"; } 2>&1 | tail -n1 >>benchmark_results.txt
    echo "Hadoop" >>benchmark_results.txt
    # Run hadoop command
    { /usr/bin/time -q -f "%e" /usr/local/hadoop-3.3.4/bin/hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-map/reduce-examples-3.3.4.jar wordcount "input/$FILE" output; } 2>&1 | tail -n1 >>benchmark_results.txt
    # Cleanup output folder
    /usr/local/hadoop-3.3.4/bin/hdfs dfs -rm -r output
  done
done

# Cleanup input and text files folders
/usr/local/hadoop-3.3.4/bin/hdfs dfs -rm -r input
sudo rm -r text_files
