from fastapi import FastAPI, HTTPException
from common import defines
import httpx

messanger_service = FastAPI()

@messanger_service.get("/messenger")
async def compose_data() -> str:
    return "[Messenger is not yet implemented]"
