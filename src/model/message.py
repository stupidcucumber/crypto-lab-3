import enum
from pydantic import BaseModel


class MessageType(enum.IntEnum):
    INITIAL_EXCHANGE: int = 0
    COMPUTE: int = 1
    COMPUTED: int = 2
    CLIENTS_CHANGED: int = 3
    UPDATE_KEY: int = 4
    MESSAGE: int = 5
    DISCONNECT: int = 6
    

class OrdinaryMessageContent(BaseModel):
    fromUser: str
    message: str


class ClientsChangedContent(BaseModel):
    p: int
    g: int
    clients: list[str]


class InitialExchangeContent(BaseModel):
    p: int
    g: int
    

class IntroductionContent(BaseModel):
    client: str
    
    
class OrdinaryContent(BaseModel):
    fromUser: str
    message: bytes
    
    
class UpdateKeyContent(BaseModel):
    fromUser: str
    toUser: str
    
    
class ComputeContent(BaseModel):
    fromUser: str
    toUser: str
    public: int

    
class Message(BaseModel):
    type: MessageType
    content: ClientsChangedContent | InitialExchangeContent | IntroductionContent | OrdinaryContent | ComputeContent | UpdateKeyContent | None = None