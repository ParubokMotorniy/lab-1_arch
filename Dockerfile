FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip bash curl python3.12-venv wget\
    zsh

RUN wget -qO - https://repository.hazelcast.com/api/gpg/key/public | gpg --dearmor | tee /usr/share/keyrings/hazelcast-archive-keyring.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/hazelcast-archive-keyring.gpg] https://repository.hazelcast.com/debian stable main" | tee -a /etc/apt/sources.list && \
    apt-get update && apt-get install hazelcast=5.5.0 -y

WORKDIR /app

RUN python3 -m venv ./meow
RUN . ./meow/bin/activate 
RUN ./meow/bin/pip install "fastapi[standard]" hazelcast-python-client

COPY deployment.sh /app/deployment.sh
RUN mkdir /app/services
RUN mkdir /app/common
RUN touch __init__.py

COPY services/* /app/services
COPY common/* /app/common

RUN chmod +x /app/deployment.sh
RUN chsh -s $(which zsh)

CMD ["/bin/zsh", "/app/deployment.sh", "3"]
