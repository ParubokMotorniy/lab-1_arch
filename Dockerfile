FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip bash curl python3.12-venv 

WORKDIR /app

RUN python3 -m venv ./meow
RUN . ./meow/bin/activate 
RUN ./meow/bin/pip install "fastapi[standard]"

COPY deployment.sh /app/deployment.sh
RUN mkdir /app/services
RUN mkdir /app/common
RUN touch __init__.py

COPY services/* /app/services
COPY common/* /app/common

RUN chmod +x /app/deployment.sh

CMD ["/bin/bash", "/app/deployment.sh"]
