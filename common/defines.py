from pydantic import BaseModel

class SimpleMessage(BaseModel):
    msg: str

class SimpleTaggedMessage(BaseModel):
    msg: str
    uuid: int

