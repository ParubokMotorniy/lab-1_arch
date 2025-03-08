from fastapi import FastAPI, HTTPException
import hazelcast
from ..common import defines
import os

hz_cluster_name = os.environ["CLUSTER_NAME"]
hz_client = hazelcast.HazelcastClient(
    cluster_name=hz_cluster_name, 
)

hz_map = hz_client.get_map("map-messages").blocking()

logger_service = FastAPI()

@logger_service.get("/logger")
async def ping_get():
    return

@logger_service.post("/logger/store-msg")
async def post_message(new_msg: defines.SimpleTaggedMessage):
    if hz_map.contains_key(new_msg.uuid):
        raise HTTPException(status_code=403, detail="Error: An attempt to insert a duplicate message ID occurred!") #uuids do guarantee uniqueness, but the seas of web are really choppy
    hz_map.put(new_msg.uuid, new_msg.msg)
    return

@logger_service.get("/logger/get-msgs", response_model=defines.SimpleMessageCollection)
def get_stored_messages():
    return defines.SimpleMessageCollection(msgs=[entry[1] for entry in hz_map.entry_set()])
