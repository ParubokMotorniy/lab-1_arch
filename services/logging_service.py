from fastapi import FastAPI, HTTPException
import hazelcast
from ..common import defines
import os
import subprocess

hz_cluster_name = os.environ["CLUSTER_NAME"]

logger_service = FastAPI()

logger_service.state.hz_client = None
logger_service.state.hz_map = None
logger_service.hz_node = None

@logger_service.on_event("shutdown")
async def close_hz():
    logger_service.state.hz_client.shutdown()
    logger_service.state.hz_node.terminate()
    logger_service.state.hz_node.wait()
    print(f"Logger {os.getpid()} terminated!")

@logger_service.on_event("startup")
async def start_hz():
    logger_service.state.hz_node = subprocess.Popen(["hz", "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    logger_service.state.hz_client = hazelcast.HazelcastClient(
        cluster_name=hz_cluster_name, 
    )

    logger_service.state.hz_map = logger_service.state.hz_client.get_map("map-messages").blocking()

    print(f"Logger {os.getpid()} started!")

@logger_service.get("/logger")
async def ping_get():
    return

@logger_service.post("/logger/store-msg")
async def post_message(new_msg: defines.SimpleTaggedMessage):
    print(f"Logger {os.getpid()} received a message: {new_msg.msg}")
    if logger_service.state.hz_map.contains_key(new_msg.uuid):
        raise HTTPException(status_code=403, detail="Error: An attempt to insert a duplicate message ID occurred!") #uuids do guarantee uniqueness, but the seas of web are really choppy
    logger_service.state.hz_map.put(new_msg.uuid, new_msg.msg)
    return

@logger_service.get("/logger/get-msgs", response_model=defines.SimpleMessageCollection)
def get_stored_messages():
    return defines.SimpleMessageCollection(msgs=[entry[1] for entry in logger_service.state.hz_map.entry_set()])
