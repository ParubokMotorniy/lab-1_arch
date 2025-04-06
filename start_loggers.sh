#!/bin/sh

#args: num-loggers hz-cluster-name start-port

num_loggers=${1:-1}

num_loggers_created=0

log_hosts=""

if [ 1 -lt $# ]; then
    export CLUSTER_NAME="$2"
else
    export CLUSTER_NAME="dev"
fi

start_port=${3}

while [ "$num_loggers_created" -lt "$num_loggers" ]; do
    port=$((start_port + num_loggers_created))

    fastapi dev --port "${port}" ./logging/logging_service.py &

    log_hosts="${log_hosts} http://127.0.0.1:${port}"

    num_loggers_created=$((num_loggers_created + 1))
done

echo "LOG_HOSTS=$log_hosts"
