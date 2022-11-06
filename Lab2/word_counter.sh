#!/usr/bin/env bash

#install matplotlib to plot the performance graphs
pip3 install matplotlib

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
/usr/local/hadoop-3.3.4/bin/hdfs dfs -mkdir input

# Retrieve wordcount.py path
WORD_COUNT_PYSPARK=`sudo find / -name wordcount.py`

# repeat three times to obtain an average
for i in 1 2 3
do
# Copy files into hadoop file system and process input files in text_files directory
  for FILE in `ls text_files/* | cut -d"/" -f2`
  do
    /usr/local/hadoop-3.3.4/bin/hdfs dfs -mkdir output
    /usr/local/hadoop-3.3.4/bin/hdfs dfs -copyFromLocal "text_files/$FILE" input
    echo "$FILE" >>LOG_FILE
    echo "Spark" >>LOG_FILE
    # Run spark command
    { time python3 "$WORD_COUNT_PYSPARK" "text_files/$FILE"; } 2>&1 | tail -n3 | head -n1 | sed -e 's/\<real\>//g' | tr  -d '[:blank:]'>>LOG_FILE
    echo "Hadoop" >>LOG_FILE
    # Run hadoop command
    { time /usr/local/hadoop-3.3.4/bin/hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-map/reduce-examples-3.3.4.jar wordcount "input/$FILE" output; } 2>&1 | tail -n3 | head -n1 | sed -e 's/\<real\>//g' | tr  -d '[:blank:]'>>LOG_FILE
    # Cleanup output folder
    /usr/local/hadoop-3.3.4/bin/hdfs dfs -rm -r output
  done
done

# Cleanup input and text files folders
/usr/local/hadoop-3.3.4/bin/hdfs dfs -rm -r input
sudo rm -r text_files
