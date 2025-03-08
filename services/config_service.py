from fastapi import FastAPI, HTTPException
from fastapi.logger import logger
from ..common import defines
import httpx
import os

config_service = FastAPI()

config_service.state.service_to_try_idx = 0
config_service.state.available_logger_hosts = []

@config_service.on_event("startup")
async def load_config():
    config_service.state.available_logger_hosts = os.environ["LOG_HOSTS"].strip().split()

    logger.info(f"Static logging hosts: {config_service.state.available_logger_hosts}")

async def is_logger_alive(logger_url: str, client: httpx.AsyncClient) -> bool:
    try:
        logger.info(f"Pinging logger: {logger_url}")
        response = await client.get(logger_url, timeout=10)
        return response.status_code == 200
    except httpx.RequestError as e:
        logger.warning(f"Logger {logger_url} is unavailable: {e}")
        return False

def get_next_logger() -> str:
    config_service.state.service_to_try_idx = (
        config_service.state.service_to_try_idx + 1
    ) % len(config_service.state.available_logger_hosts)

    return config_service.state.available_logger_hosts[config_service.state.service_to_try_idx]

@config_service.get("/config")
def ping_get():
    return

@config_service.get("/config/logger_hosts", response_model=str)
async def get_available_logger() -> str:
    async with httpx.AsyncClient() as client:
        for _ in range(len(config_service.state.available_logger_hosts)):
                logger_host = get_next_logger()
                logger_to_try = f"{logger_host}/logger"

                if await is_logger_alive(logger_to_try, client):
                    logger.info(f"Found available host: {logger_host}")
                    return logger_host
    return ""
