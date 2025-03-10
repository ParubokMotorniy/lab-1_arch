#!/bin/sh

. ./meow/bin/activate

num_loggers=${1:-1}

num_loggers_created=0
log_hosts=""

if [ 1 -lt $# ]; then
    export CLUSTER_NAME="$2"
else
    export CLUSTER_NAME="dev"
fi

while [ "$num_loggers_created" -lt "$num_loggers" ]; do
    sleep 3

    port=$((7000 + num_loggers_created))

    echo "My port: ${port}"

    fastapi dev --port "${port}" ./services/logging_service.py &

    log_hosts="${log_hosts} http://127.0.0.1:${port}"

    num_loggers_created=$((num_loggers_created + 1))
done

export LOG_HOSTS="$log_hosts"

messages_port=$((7000 + num_loggers_created))
export MESSAGE_HOST="http://127.0.0.1:${messages_port}"
fastapi dev --port "$messages_port" ./services/messages_service.py &

config_port=$((messages_port + 1))
export CONFIG_HOST="http://127.0.0.1:${config_port}"
fastapi dev --port "$config_port" ./services/config_service.py &

facade_port=$((config_port + 1))
fastapi dev --port "$facade_port" ./services/facade_service.py &
