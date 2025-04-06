#!/bin/sh

num_loggers=${1:-1}
num_messengers=${2:-1}

num_loggers_created=0
num_messengers_created=0

message_hosts=""
log_hosts=""

if [ 1 -lt $# ]; then
    export CLUSTER_NAME="$3"
else
    export CLUSTER_NAME="dev"
fi

while [ "$num_loggers_created" -lt "$num_loggers" ]; do
    port=$((7000 + num_loggers_created))

    echo "Logger port: ${port}"

    fastapi dev --port "${port}" ./logging/logging_service.py &

    log_hosts="${log_hosts} http://127.0.0.1:${port}"

    num_loggers_created=$((num_loggers_created + 1))
done

export LOG_HOSTS="$log_hosts"
export MESSAGING_KAFKA_TOPIC="user-post-topic"

while [ ${num_messengers_created} -lt ${num_messengers} ];do
    port=$((7000 + num_loggers_created + num_messengers_created))

    echo "Messenger port: ${port}"

    fastapi dev --port "${port}" ./messages/messages_service.py &

    message_hosts="${message_hosts} http://127.0.0.1:${port}"

    num_messengers_created=$((num_messengers_created + 1))
done

export MESSAGE_HOSTS="${message_hosts}"

config_port=$((7000 + num_loggers + num_messengers))
export CONFIG_HOST="http://127.0.0.1:${config_port}"
fastapi dev --port "$config_port" ./core/config_service.py &

facade_port=$((config_port + 1))
fastapi dev --port "$facade_port" ./core/facade_service.py &
