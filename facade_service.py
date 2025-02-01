from fastapi import FastAPI, HTTPException
from common import defines
from common import hosts
import httpx
import uuid

facade_service = FastAPI()

@facade_service.post("/facade")
async def post_message(plain_msg: str):
    newMsg = defines.SimpleTaggedMessage(plain_msg, uuid.uuid4)
    async with httpx.AsyncClient() as client:
        logger_response = await client.post(f"{hosts.logger_address}/logger/store-msg", json=newMsg.model_dump_json())
    return logger_response

@facade_service.get("/facade", response_model=list(str))
async def compose_data():
    logger_data = None
    messenger_data = None
    async with httpx.AsyncClient() as client:
        logger_data = await client.get(f"{hosts.logger_address}/logger/get-msgs")
        messenger_data = await client.get(f"{hosts.messenger_address}/messenger/")

    if messenger_data == None or logger_data == None:
        raise HTTPException(status_code=500, detail="Error: Failed to obtain data from!") 
    
    logger_data.append(messenger_data)

    return logger_data
