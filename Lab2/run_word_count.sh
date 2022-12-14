#!/usr/bin/env bash

WORKDIR=$(cd "$(dirname "$0")" && pwd)
export WORKDIR


VENV=$(realpath "$PWD")/venv
if [[ ! -d $VENV ]]; then
    virtualenv -p python3 "$VENV" || python3 -m venv "$VENV"
fi

activate_venv() {
    # shellcheck source=/dev/null
    source "$WORKDIR/venv/bin/activate"
}

# Source code dependencies
echo "Installing dependencies"
activate_venv && pip3 install -r requirements.txt

# Create instance
activate_venv && python setup_instance.py


source env_variables.txt
echo "INSTANCE_IP=$INSTANCE_IP"
echo "PRIVATE_KEY_FILE=$PRIVATE_KEY_FILE"
chmod 600 "$PRIVATE_KEY_FILE"

# Even though we wait for the instance to be running in python, openssh takes some time to start.
# We check port 22 every 5s to see if sshd started on our instance, before trying to ssh into it.
SSH_IS_NOT_RUNNING=1
while [[ $SSH_IS_NOT_RUNNING -eq 1 ]]; do
    # if exit code of nc is 0, ssh started, else if it is 1, ssh is not started.
    nc -vzw 1 "$INSTANCE_IP" 22
    SSH_IS_NOT_RUNNING=$?
    if [[ $SSH_IS_NOT_RUNNING -eq 1 ]]; then
        echo "ssh not started yet, trying again in 3s..."; 
        sleep 3s;
    else
        echo "ssh started.";
    fi
done


# What is done here :
#    - Clone our public repo that contains our MapReduce algorithm, the dataset, and the hadoop installation script
#    - Install hadoop and configure it properly
#    - Compile our MapReduce to a jar file
#    - Create an input directory in hadoop filesystem with hdfs
#    - Unzip the dataset, and copy it to this input directory
#    - Run our MapReduce with hadoop on our dataset
#    - List the outputted files (located in the output folder)
#    - Print them to the terminal
ssh -o "StrictHostKeyChecking no" -i "$PRIVATE_KEY_FILE" ubuntu@"$INSTANCE_IP" '
    set -x && \
    git clone https://github.com/PhilippPeron/advanced-cloud-log8415.git source_code && \
    chmod +x source_code/Lab2/install-hadoop-spark.sh && \
    sh source_code/Lab2/install-hadoop-spark.sh && \
    source ~/.profile && \
    chmod +x source_code/Lab2/word_counter.sh && \
    sh source_code/Lab2/word_counter.sh && \

    '
