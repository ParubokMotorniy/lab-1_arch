from fastapi import FastAPI, HTTPException
from confluent_kafka import Producer
from ..common import defines
from ..common import funcs
import httpx
import uuid
import os
import numpy as np

facade_service = FastAPI()

facade_service.state.kafka_producer = None
facade_service.state.messaging_topic = ""

def delivery_callback(err, msg):
    if err:
        print(f'ERROR: Message delivery failed with message: {err}')
    else:
        print(f"Produced event to topic {msg.topic()}: key = {msg.key().decode('utf-8')} value = {msg.value().decode('utf-8')}")

@facade_service.on_event("startup")
async def load_config():
    facade_config = funcs.read_value_for_key("facade_config")
    
    facade_service.state.messaging_topic = facade_config['topic_name']
    facade_service.state.kafka_producer = Producer(facade_config['kafka_config'])
    
    funcs.register_consul_service("facade", "0", os.environ["INSTANCE_HOST"], int(os.environ["INSTANCE_PORT"]), 30, 60, "/health" )

    print(f"Facade service {os.getpid()} started!")


async def get_available_logger(client: httpx.AsyncClient):
    available_loggers = funcs.query_consul_services("logger")
    
    if len(available_loggers) == 0:
        return ""
    
    host, port, id = available_loggers[np.random.choice(len(available_loggers))]
    
    print(f"Found healthy logger instance with id `{id}`:{host}:{port}")
    
    return f"http://{host}:{port}"

@facade_service.get("/health")
async def check():
    return "Facade is healthy"

async def get_available_random_messenger(client: httpx.AsyncClient):
    available_loggers = funcs.query_consul_services("messenger")
    
    if len(available_loggers) == 0:
        return ""
    
    host, port, id = available_loggers[np.random.choice(len(available_loggers))]
    
    print(f"Found healthy messenger instance with id `{id}`:{host}:{port}")
    
    return f"http://{host}:{port}"

@facade_service.post("/facade")
async def post_message(plain_msg: defines.SimpleMessage):
    new_msg = defines.SimpleTaggedMessage(msg=plain_msg.msg, uuid=str(uuid.uuid4()))

    #forwarding to messages service
    try:
        facade_service.state.kafka_producer.produce(facade_service.state.messaging_topic, new_msg.msg, new_msg.uuid, callback=delivery_callback)
    except Exception as e:
        raise HTTPException(status_code=503, detail="Failed to forward message to messages service!")
        
    facade_service.state.kafka_producer.poll(100)
    facade_service.state.kafka_producer.flush()

    #forwarding to logger
    async with httpx.AsyncClient() as client:
        try:
            logger_host = await get_available_logger(client)

            if len(logger_host) != 0:
                print(f"Storing message to logger: {logger_host}")
                logger_response = await client.post(
                    f"{logger_host}/logger/store-msg",
                    json=new_msg.model_dump(),
                    timeout=20
                )
                return logger_response.status_code
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Failed to send message to config server or logger instance: {e}")

    raise HTTPException(status_code=503, detail="No logger services available")

@facade_service.get("/facade", response_model=list[str])
async def get_messages():
    logger_data = None
    messenger_data = None

    async with httpx.AsyncClient() as client:
        logger_host = await get_available_logger(client)

        if len(logger_host) != 0:
            try:
                logger_data = await client.get(f"{logger_host}/logger/get-msgs", timeout=30)
            except httpx.RequestError as e:
                print(f"Failed to fetch messages from {logger_host}: {e}")

        messenger_host = await get_available_random_messenger(client)
        if len(messenger_host) != 0:
            try:
                messenger_data = await client.get(f"{messenger_host}/messenger/messages", timeout=10)
            except httpx.RequestError as e:
                print(f"Failed to fetch messages from messenger {messenger_host}: {e}")

    print(messenger_data, logger_data)
    if (
        (messenger_data != None and messenger_data.status_code != 200) or (logger_data != None and logger_data.status_code != 200)
    ):
        raise HTTPException(status_code=500, detail="Error: Failed to obtain messages!") 

    messenger_str = messenger_data.text if messenger_data else ""
    logger_messages = defines.SimpleMessageCollection.model_validate_json(logger_data.text).msgs if logger_data else []
    
    messages_dict = {"Loggers:":logger_messages, "Messengers:":messenger_str.replace('\"','')}

    return [str(messages_dict)]
