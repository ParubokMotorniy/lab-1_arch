#!/bin/sh

num_loggers=${1:-1}
num_messengers=${2:-1}

num_loggers_created=0
num_messengers_created=0

message_hosts=""
log_hosts=""

if [ 2 -lt $# ]; then
    export CLUSTER_NAME="$3"
else
    export CLUSTER_NAME="dev"
fi

if [ 3 -lt $# ]; then
    export MESSAGING_KAFKA_TOPIC="$4"
else
    export MESSAGING_KAFKA_TOPIC="user-post-topic"
fi

export CONSUL_HOST="127.0.0.1"
export CONSUL_PORT="8500"

while [ "$num_loggers_created" -lt "$num_loggers" ]; do
    port=$((7000 + num_loggers_created))

    echo "Logger port: ${port}"

    INSTANCE_PORT=${port} INSTANCE_HOST="127.0.0.1" fastapi dev --port "${port}" ./logging/logging_service.py &

    log_hosts="${log_hosts} http://127.0.0.1:${port}"

    num_loggers_created=$((num_loggers_created + 1))
done

export LOG_HOSTS="$log_hosts"

while [ ${num_messengers_created} -lt ${num_messengers} ];do
    port=$((7000 + num_loggers_created + num_messengers_created))

    echo "Messenger port: ${port}"

    INSTANCE_PORT=${port} INSTANCE_HOST="127.0.0.1" fastapi dev --port "${port}" ./messages/messages_service.py &

    message_hosts="${message_hosts} http://127.0.0.1:${port}"

    num_messengers_created=$((num_messengers_created + 1))
done

export MESSAGE_HOSTS="${message_hosts}"

facade_port=$((7000 + num_loggers + num_messengers))
INSTANCE_PORT=${port} INSTANCE_HOST="127.0.0.1" fastapi dev --port "$facade_port" ./core/facade_service.py &

