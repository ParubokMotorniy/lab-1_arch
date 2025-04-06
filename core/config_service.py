from fastapi import FastAPI, HTTPException
from ..common import defines
import httpx
import os
import random as rnd

config_service = FastAPI()

config_service.state.service_to_try_idx = 0
config_service.state.available_logger_hosts = []
config_service.state.available_message_hosts = []

@config_service.on_event("startup")
async def load_config():
    config_service.state.available_logger_hosts = os.environ["LOG_HOSTS"].strip().split()
    config_service.state.available_message_hosts = os.environ["MESSAGE_HOSTS"].strip().split()

    print(f"Static logging hosts: {config_service.state.available_logger_hosts}")
    print(f"Static message hosts: {config_service.state.available_message_hosts}")
    
    print("Config service started!")
    
async def is_host_alive(host_ping_url: str, client: httpx.AsyncClient) -> bool:
    try:
        print(f"Pinging host: {host_ping_url}")
        response = await client.get(host_ping_url, timeout=10)
        return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Host {host_ping_url} is unavailable: {e}")
        return False

def get_next_logger() -> str:
    config_service.state.service_to_try_idx = (
        config_service.state.service_to_try_idx + 1
    ) % len(config_service.state.available_logger_hosts)

    return config_service.state.available_logger_hosts[config_service.state.service_to_try_idx]

def get_random_messenger() -> str:
    return config_service.state.available_message_hosts[rnd.randint(0, len(config_service.state.available_message_hosts)-1)]

@config_service.get("/config")
def ping_get():
    return

@config_service.get("/config/logger_hosts", response_model=str)
async def get_available_logger() -> str:
    async with httpx.AsyncClient() as client:
        for _ in range(len(config_service.state.available_logger_hosts)):
                logger_host = get_next_logger()
                logger_to_try = f"{logger_host}/logger"

                if await is_host_alive(logger_to_try, client):
                    print(f"Found available logger: {logger_host}")
                    return logger_host
    return ""

@config_service.get("/config/message_hosts", response_model=str)
async def get_available_messenger(max_attempts: int) -> str:
    async with httpx.AsyncClient() as client:
        for _ in range(max_attempts):
                messenger_host = get_random_messenger()
                messenger_to_try = f"{messenger_host}/messenger"
                
                if await is_host_alive(messenger_to_try, client):
                    print(f"Found available messenger: {messenger_to_try}")
                    return messenger_host
    return ""
