import socket, json, random, base64
from .model import (
    Message,
    MessageType,
    IntroductionContent,
    ComputeContent,
    UpdateKeyContent,
    OrdinaryMessageContent
)
from .utils import encrypt_aes, decrypt_aes


class Client:
    def __init__(self, name: str, port: int, logs: bool = True) -> None:
        self.clients: list[str] | None = None
        self.logs = logs
        self.p: int = 0
        self.g: int = 0
        self.a: int = random.randint(2, 1000000)
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
    
    def _send_disconnect(self) -> None:
        self._send(
            message=Message(
                type=MessageType.DISCONNECT
            )
        )
    
    def my_index(self) -> int:
        for index, c_name in enumerate(self.clients):
            if c_name == self.name:
                return index
        return -1
    
    def calculate_shared(self) -> int:
        shared = self.g
        for to_user in self.clients:
            if to_user == self.name:
                continue
            self._send(
                message=Message(
                    type=MessageType.COMPUTE,
                    content=ComputeContent(
                        fromUser=self.name,
                        toUser=to_user,
                        public=shared
                    )
                )
            )
            response: Message = self._read()
            if response.type != MessageType.COMPUTED:
                raise ValueError('Must be computed, but ', response)
            shared = response.content.public
        shared = pow(shared, self.a, self.p).to_bytes(length=(shared.bit_length() + 7) // 8, byteorder='little')
        if self.logs:
            print('Calculated the following shared number: ', shared)
        my_index = self.my_index()
        if my_index >= len(self.clients) - 1:
            return shared
        else:
            self._send(
                message=Message(
                    type=MessageType.UPDATE_KEY,
                    content=UpdateKeyContent(
                        fromUser=self.name,
                        toUser=self.clients[my_index + 1]
                    )
                )
            )
        return shared
    
    def communicate_forever(self) -> None:
        # Accept initial message from the server
        initial_request: Message = self._read()
        if initial_request.type != MessageType.INITIAL_EXCHANGE:
            raise ValueError('Expected INITIAL_EXCHANGE message type, but got: ', initial_request)
        self.p = initial_request.content.p
        self.g = initial_request.content.g
        self._send(
            message=Message(
                type=MessageType.INITIAL_EXCHANGE,
                content=IntroductionContent(client=self.name)
            )
        )
        
        # Accepting requests from the server
        while True:
            request: Message = self._read()
            if self.logs:
                print(request)

            if request.type == MessageType.COMPUTE:
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
                
            elif request.type == MessageType.BROADCAST_MESSAGE:
                message = decrypt_aes(key=self.shared, ciphertext=request.content.message.encode())
                print('%s >  %s' % (request.content.fromUser, message))

            elif request.type == MessageType.CLIENTS_CHANGED:
                self.clients = request.content.clients
                if self.clients[0] != self.name:
                    continue
                self.shared = self.calculate_shared()

            elif request.type == MessageType.UPDATE_KEY:
                self.shared = self.calculate_shared()
                
    def send_message_forever(self) -> None:
        while True:
            message: str = input()
            encoded_message = encrypt_aes(self.shared, plaintext=message)
            self._send(
                message=Message(
                    type=MessageType.BROADCAST_MESSAGE,
                    content=OrdinaryMessageContent(
                        fromUser=self.name,
                        message=base64.b64encode(encoded_message).decode()
                    )
                )
            )
            
    def try_send_message_forever(self) -> None:
        try:
            self.send_message_forever()
        except KeyboardInterrupt as e:
            pass
        except:
            pass

    def try_commucate_forever(self) -> None:
        try:
            self.communicate_forever()
        except KeyboardInterrupt as e:
            print('Disconnecting from the server.')
            self._send_disconnect()
        except Exception as e:
            print('Server is down.', e)
            