For the app to run you must have the following installed:
* FastApi + Hazelcast client: `pip install "fastapi[standard]" hazelcast-python-client`
* Hazelcast: `wget -qO - https://repository.hazelcast.com/api/gpg/key/public | gpg --dearmor | tee /usr/share/keyrings/hazelcast-archive-keyring.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/hazelcast-archive-keyring.gpg] https://repository.hazelcast.com/debian stable main" | tee -a /etc/apt/sources.list && \
    apt-get update && apt-get install hazelcast=5.5.0 -y`
* Kafka in any form
* Kafka Python client: `pip install confluent-kafka`

There are also some scripts to aid the startup:
* `deployment.sh` : starts all services.
* `start_loggers.sh` : only starts loggers.
* `start_messengers` : only starts messengers.
* `start_core.sh` : only starts facade and config services.
  
Please, note that services rely on some environment variables to have been defined (when starting via individual scripts).

In the `kafka-servers` directory you will find the config files I used for the configuration of Kafka nodes (not that that the topic `user-post-topic` is used internally by microservices so make sure one has been added to the cluster).