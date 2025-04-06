#!/bin/sh

#args: num-messengers start-port
#make sure MESSAGING_KAFKA_TOPIC has been exported

num_messengers=${1:-1}
start_port=${2}

num_messengers_created=0
message_hosts=""

while [ ${num_messengers_created} -lt ${num_messengers} ];do
    port=$((start_port + + num_messengers_created))

    fastapi dev --port "${port}" ./messages/messages_service.py &

    message_hosts="${message_hosts} http://127.0.0.1:${port}"

    num_messengers_created=$((num_messengers_created + 1))
done

echo "MESSAGE_HOSTS=${message_hosts}"
