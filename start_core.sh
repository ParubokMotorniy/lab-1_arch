#!/bin/sh

#args: start-port
#make sure MESSAGE_HOSTS and LOG_HOSTS have been exported

start_port=${1}

config_port=${start_port}
export CONFIG_HOST="http://127.0.0.1:${config_port}"
fastapi dev --port "$config_port" ./core/config_service.py &

facade_port=$((config_port + 1))
fastapi dev --port "$facade_port" ./core/facade_service.py &
