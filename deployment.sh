#!/bin/sh
# . ./meow/bin/activate

num_loggers=${1:-1}

num_loggers_created=0
log_hosts=""

export CLUSTER_NAME="hazelcast-test"

while [ "$num_loggers_created" -lt "$num_loggers" ]; do
    hz start &

    sleep 7

    port=$((7000 + num_loggers_created))

    echo "My port: ${port}"

    fastapi dev --port "${port}" ./services/logging_service.py &

    log_hosts="${log_hosts} http://127.0.0.1:${port}"

    num_loggers_created=$((num_loggers_created + 1))
done

export LOG_HOSTS="$log_hosts"

# Start the messages service
messages_port=$((7000 + num_loggers_created))
export MESSAGE_HOST="http://127.0.0.1:${messages_port}"
fastapi dev --port "$messages_port" ./services/messages_service.py &

config_port=$((messages_port + 1))
export CONFIG_HOST="http://127.0.0.1:${config_port}"
fastapi dev --port "$config_port" ./services/config_service.py &

# Start the facade service
facade_port=$((config_port + 1))
fastapi dev --port "$facade_port" ./services/facade_service.py &
