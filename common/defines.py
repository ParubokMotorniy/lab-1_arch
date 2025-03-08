from pydantic import BaseModel
import uuid

class SimpleMessage(BaseModel):
    msg: str

class SimpleMessageCollection(BaseModel):
    msgs: list[str]

class SimpleTaggedMessage(BaseModel):
    msg: str
    uuid: str


