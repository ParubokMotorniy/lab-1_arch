from fastapi import FastAPI, HTTPException
from ..common import defines

stored_messages = dict()

logger_service = FastAPI()

@logger_service.post("/logger/store-msg")
async def post_message(new_msg: defines.SimpleTaggedMessage):
    if new_msg.uuid in stored_messages.keys():
        raise HTTPException(status_code=403, detail="Error: An attempt to insert a duplicate message ID occurred!") #uuids do guarantee uniqueness, but the seas of web are really choppy
    stored_messages[new_msg.uuid] = new_msg.msg
    return

@logger_service.get("/logger/get-msgs", response_model=defines.SimpleMessageCollection)
def get_stored_messages():
    return defines.SimpleMessageCollection(msgs=stored_messages.values())
