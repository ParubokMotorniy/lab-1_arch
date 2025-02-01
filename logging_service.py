from fastapi import FastAPI, HTTPException
from common import defines
import httpx

stored_messages = dict()

logger_service = FastAPI()

@logger_service.post("/logger/store-msg")
async def post_message(plain_msg: str, new_msg: defines.SimpleTaggedMessage):
    if new_msg.uuid in stored_messages.keys():
        raise HTTPException(status_code=403, detail="Error: An attempt to insert a duplicate message ID occurred!") #uuids do guarantee uniqueness, but the seas of web are really choppy
    stored_messages[new_msg.uuid] = new_msg.msg
    return

@logger_service.get("/logger/get-msgs", response_model=list(defines.SimpleMessage))
async def compose_data():
    stripped_msgs = [msg.msg for msg in stored_messages.values()]
    return stripped_msgs
