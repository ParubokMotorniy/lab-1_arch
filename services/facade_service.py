from fastapi import FastAPI, HTTPException
from fastapi.logger import logger
from ..common import defines
import httpx
import uuid
import os

facade_service = FastAPI()

facade_service.state.messages_host = ""
facade_service.state.config_host = ""

@facade_service.on_event("startup")
async def load_config():
    facade_service.state.messages_host = os.environ["MESSAGE_HOST"].strip()
    facade_service.state.config_host = os.environ["CONFIG_HOST"].strip()

    logger.info(f"Messages host: {facade_service.state.messages_host}")
    logger.info(f"Config host: {facade_service.state.config_host}")

async def get_available_logger(client: httpx.AsyncClient):
    config_response = await client.get(f"{facade_service.state.config_host}/config/logger_hosts")

    if config_response.status_code != 200:
        return ""
    
    return config_response.text.replace('\"','')

@facade_service.post("/facade")
async def post_message(plain_msg: defines.SimpleMessage):
    new_msg = defines.SimpleTaggedMessage(msg=plain_msg.msg, uuid=str(uuid.uuid4()))

    async with httpx.AsyncClient() as client:
        try:
            logger_host = await get_available_logger(client)

            if len(logger_host) != 0:
                logger.info(f"Storing message to logger: {logger_host}")
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
                logger.warning(f"Failed to fetch messages from {logger_host}: {e}")

        try:
            messenger_data = await client.get(f"{facade_service.state.messages_host}/messenger", timeout=30)
        except httpx.RequestError as e:
            logger.warning(f"Failed to fetch messages from messenger: {e}")

    print(messenger_data, logger_data)
    if (
        (messenger_data != None and messenger_data.status_code != 200) or (logger_data != None and logger_data.status_code != 200)
    ):
        raise HTTPException(status_code=500, detail="Error: Failed to obtain messages!") 

    messenger_str = messenger_data.text if messenger_data else ""
    logger_messages = defines.SimpleMessageCollection.model_validate_json(logger_data.text).msgs if logger_data else []
    logger_messages.append(messenger_str)

    return logger_messages
