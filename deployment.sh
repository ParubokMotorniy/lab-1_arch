#!/bin/sh

#only two arguments expectes: number of loggers and number of messengers

num_loggers=${1:-1}
num_messengers=${2:-1}

num_loggers_created=0
num_messengers_created=0

export CONSUL_HOST="127.0.0.1"
export CONSUL_PORT="8500"

curl -X PUT --data @configs/facade_kafka_config.cfg http://"$CONSUL_HOST":"$CONSUL_PORT"/v1/kv/facade_config
curl -X PUT --data @configs/logger_hz_config.cfg http://"$CONSUL_HOST":"$CONSUL_PORT"/v1/kv/logger_config
curl -X PUT --data @configs/messenger_kafka_config.cfg http://"$CONSUL_HOST":"$CONSUL_PORT"/v1/kv/messenger_config

while [ "$num_loggers_created" -lt "$num_loggers" ]; do
    port=$((7000 + num_loggers_created))

    echo "Logger port: ${port}"

    INSTANCE_PORT=${port} INSTANCE_HOST="127.0.0.1" fastapi dev --port "${port}" ./logging/logging_service.py &

    num_loggers_created=$((num_loggers_created + 1))
done


while [ ${num_messengers_created} -lt ${num_messengers} ];do
    port=$((7000 + num_loggers_created + num_messengers_created))

    echo "Messenger port: ${port}"

    INSTANCE_PORT=${port} INSTANCE_HOST="127.0.0.1" fastapi dev --port "${port}" ./messages/messages_service.py &

    num_messengers_created=$((num_messengers_created + 1))
done


facade_port=$((7000 + num_loggers + num_messengers))
INSTANCE_PORT=${port} INSTANCE_HOST="127.0.0.1" fastapi dev --port "$facade_port" ./core/facade_service.py &

