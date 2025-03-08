from fastapi import FastAPI, HTTPException
from ..common import defines
import httpx
import uuid
import os

facade_service = FastAPI()

available_logger_hosts=os.environ["LOG_HOSTS"].strip().split(' ')
messages_host = os.environ["MESSAGE_HOST"].strip()

print(f"Static logging hosts: {available_logger_hosts}")
print(f"Messages host: {messages_host}")

async def if_logger_alive(logger_url: str, client:  httpx.AsyncClient):
    print(f"Pinging logger: {logger_url}")
    ping_response = await client.get(logger_url, timeout=7) #merely pinging a logger
    print(f"Logger response: {ping_response}")
    return ping_response.status_code == 200

@facade_service.post("/facade")
async def post_message(plain_msg: defines.SimpleMessage):
    if not hasattr(post_message, "service_to_try_idx"):
        post_message.service_to_try_idx = 0

    post_message.service_to_try_idx = (post_message.service_to_try_idx + 1) % len(available_logger_hosts) #to make sure we don't keep sending stuff to a single logger
    new_msg = defines.SimpleTaggedMessage(msg=plain_msg.msg, uuid=str(uuid.uuid4()))

    async with httpx.AsyncClient() as client:  
        for i in range(len(available_logger_hosts)):
            logger_to_try = f"{available_logger_hosts[(post_message.service_to_try_idx + i) % len(available_logger_hosts)]}/logger"
            
            logger_alive = await if_logger_alive(logger_to_try, client)

            if(logger_alive):
                logger_to_try += "/store-msg"
                logger_response = await client.post(logger_to_try, content=new_msg.model_dump_json()) #sending actual message
                return logger_response.status_code
            
            print("Logger did not respond")

    raise HTTPException(status_code=503, detail="No logger services available")

@facade_service.get("/facade", response_model=list[str])
async def get_messages():
    logger_data = None
    messenger_data = None

    async with httpx.AsyncClient() as client:
        for i in range(len(available_logger_hosts)):
            logger_to_try = f"{available_logger_hosts[i]}/logger"
            
            logger_alive = await if_logger_alive(logger_to_try, client)

            if(logger_alive):
                logger_to_try += "/get-msgs"
                logger_data = await client.get(logger_to_try)
                break
            
        messenger_data = await client.get(f"{messages_host}/messenger")

    if messenger_data == None or logger_data == None or messenger_data.status_code != 200 or logger_data.status_code != 200:
        raise HTTPException(status_code=500, detail="Error: Failed to obtain messages!") 

    messenger_str = str(messenger_data.text)
    logger_messages = defines.SimpleMessageCollection.model_validate_json(logger_data.text).msgs
    logger_messages.append(messenger_str)

    return logger_messages

