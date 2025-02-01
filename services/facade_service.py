from fastapi import FastAPI, HTTPException
from ..common import defines
from ..common import hosts
import httpx
import uuid

facade_service = FastAPI()

@facade_service.post("/facade")
async def post_message(plain_msg: defines.SimpleMessage):
    new_msg = defines.SimpleTaggedMessage(msg=plain_msg.msg, uuid=str(uuid.uuid4()))
    async with httpx.AsyncClient() as client:
        logger_response = await client.post(f"{hosts.logger_address}/logger/store-msg", content=new_msg.model_dump_json())
    return logger_response.status_code

@facade_service.get("/facade", response_model=list[str])
async def get_messages():
    logger_data = None
    messenger_data = None

    async with httpx.AsyncClient() as client:
        logger_data = await client.get(f"{hosts.logger_address}/logger/get-msgs")
        messenger_data = await client.get(f"{hosts.messenger_address}/messenger")

    if messenger_data == None or logger_data == None:
        raise HTTPException(status_code=500, detail="Error: Failed to obtain messages!") 

    messenger_str = str(messenger_data.text)
    logger_messages = defines.SimpleMessageCollection.model_validate_json(logger_data.text).msgs
    logger_messages.append(messenger_str)

    return logger_messages
