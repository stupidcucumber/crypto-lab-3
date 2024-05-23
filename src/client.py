import socket, json, random, time
from .model import (
    Message,
    MessageType,
    IntroductionContent,
    ComputeContent
)


class Client:
    def __init__(self, name: str, port: int) -> None:
        self.clients: list[str] | None = None
        self.p: int = 0
        self.g: int = 0
        self.a: int = random.randint(20, 100)
        self.name = name
        self.socket = socket.create_connection(('', port))
        self.shared: int = None
        
    def _send(self, message: Message, expected_type: MessageType | None = None) -> Message | None:
        self.socket.send(
            message.model_dump_json().encode()
        )
        if expected_type is not None:
            response: Message = self._read()
            if response.type != expected_type:
                raise ValueError('Expected type is other from this. Received: ', response)
            return response
        
    def _read(self) -> Message | None:
        message_raw = self.socket.recv(4096).decode()
        return Message(**json.loads(message_raw))
    
    def communicate_forever(self) -> None:
        # Accept initial message from the server
        initial_request: Message = self._read()
        if initial_request.type != MessageType.INITIAL_EXCHANGE:
            raise ValueError('Expected INITIAL_EXCHANGE message type, but got: ', initial_request)
        self.p = initial_request.content.p
        self.g = initial_request.content.g
        self.clients = initial_request.content.clients
        self._send(
            message=Message(
                type=MessageType.STATUS_OK,
                content=IntroductionContent(name=self.name)
            )
        )
        
        # Accepting requests from the server
        while True:
            request: Message = self._read()

            if request.type == MessageType.COMPUTE:
                print('Received the response', request)
                self._send(
                    message=Message(
                        type=MessageType.COMPUTED,
                        content=ComputeContent(
                            fromUser=self.name,
                            toUser=request.content.fromUser,
                            public=pow(request.content.public, self.a, self.p)
                        )
                    )
                )
                
            elif request.type == MessageType.COMPUTED:
                self._send(
                    message=request
                )

            elif request.type == MessageType.USER_ADDITION:
                # Adding new user to active clients
                self.clients.append(
                    request.content.user
                )

            elif request.type == MessageType.UPDATE_KEY:
                # Calculating new shared number
                self.shared = self.g
                for to_user in self.clients:
                    print(f'{self.name} sending number to compute to {to_user}')
                    self._send(
                        message=Message(
                            type=MessageType.COMPUTE,
                            content=ComputeContent(
                                fromUser=self.name,
                                toUser=to_user,
                                public=self.shared
                            )
                        )
                    )
                    print(f'Waiting for the response from {to_user}')
                    response: Message = self._read()
                    print(f'Received response from the {to_user}')
                    if response.type != MessageType.COMPUTED:
                        raise ValueError('Must be computed, but ', response)
                    self.shared = response.content.public
                self.shared = pow(self.shared, self.a, self.p)
                print('I computed the follwing shared number: ', self.shared)
                self._send(
                    message=Message(
                        type=MessageType.UPDATING_ENDED,
                        content=IntroductionContent(
                            name=self.name
                        )
                    )
                )
                print('Sended updating ended!')
