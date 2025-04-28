For the app to run you must have the following installed:
* FastApi + Hazelcast client: `pip install "fastapi[standard]" hazelcast-python-client`
* Hazelcast: `wget -qO - https://repository.hazelcast.com/api/gpg/key/public | gpg --dearmor | tee /usr/share/keyrings/hazelcast-archive-keyring.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/hazelcast-archive-keyring.gpg] https://repository.hazelcast.com/debian stable main" | tee -a /etc/apt/sources.list && \
    apt-get update && apt-get install hazelcast=5.5.0 -y`
* Kafka running in any form 
* Kafka Python client: `pip install confluent-kafka`
* Consul running in any form

There is also `deployment.sh` script that starts all microservices (note that Kafka and Consul must be running at that moment). If you wish to change the host+port of Consul - change the self-explanatory variables in the `deployment.sh`.
  
In the `kafka-servers` directory you will find the config files I used for the configuration of Kafka nodes.

To configure how the hazelcast cluster is named or what kafka topic (or kafka node, for that matter) the microservice should use - modify the configs in `configs` folder. These are also later pushed by `deployment.sh` to the Consul instance as key-value pairs.

