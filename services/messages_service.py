from fastapi import FastAPI

messenger_service = FastAPI()

@messenger_service.get("/messenger", response_model=str)
def access_messenger() -> str:
    return "[Messenger is not yet implemented]"
