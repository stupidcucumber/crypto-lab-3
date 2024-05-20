import enum
from pydantic import BaseModel


class MessageType(enum.IntEnum):
    NONE: int = 0
    INTRODUCTION: int = 1
    INITIAL_EXCHANGE: int = 2
    ORDINARY: int = 3
    COMPUTE: int = 4
    COMPUTED: int = 5
    USER_ADDITION: int = 6 
    USER_REMOVAL: int = 7
    STATUS_OK: int = 8
    UPDATE_KEY: int = 9

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