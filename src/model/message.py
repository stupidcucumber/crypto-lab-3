import enum
from pydantic import BaseModel


class MessageType(enum.IntEnum):
    INITIAL_EXCHANGE: int = 0
    COMPUTE: int = 1
    COMPUTED: int = 2
    USER_ADDITION: int = 3
    STATUS_OK: int = 4
    UPDATE_KEY: int = 5
    UPDATING_ENDED: int = 6


class UserAdditionContent(BaseModel):
    user: str


class InitialExchangeContent(BaseModel):
    p: int
    g: int
    clients: list[str]
    

class IntroductionContent(BaseModel):
    name: str
    
    
class OrdinaryContent(BaseModel):
    fromUser: str
    message: bytes
    
    
class ComputeContent(BaseModel):
    fromUser: str
    toUser: str
    public: int

    
class Message(BaseModel):
    type: MessageType
    content: UserAdditionContent | InitialExchangeContent | IntroductionContent | OrdinaryContent | ComputeContent | None = None