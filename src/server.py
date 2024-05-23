import socket, threading, json
from .model import Message, MessageType, InitialExchangeContent, UserAdditionContent


class Server:
    def __init__(self, port: int, p: int = 23, g: int = 11) -> None:
        self.socket: socket.socket = socket.create_server(('', port))
        self.clients: dict[str, socket.socket] = dict()
        self.locks: dict[str, threading.Lock] = dict()
        self.p: int = p
        self.g: int = g
        
    def _read(self, client_socket: socket.socket) -> Message | None:
        message_raw = client_socket.recv(4096)
        message_str = message_raw.decode()
        message = Message(**json.loads(message_str))
        return message
    
    def _send(self, message: Message, client_socket: socket.socket, receiving_types: list[MessageType] | None = None) -> Message | None:
        client_socket.send(message.model_dump_json().encode())
        if receiving_types is not None:
            response: Message = self._read(client_socket=client_socket)
            if response.type not in receiving_types:
                raise ValueError('Status response is not OK. Received message: ', response)
            return response
    
    def _notificate_all(self, from_user: str, message: Message) -> None:
        for user_name, _socket in self.clients.items():
            if user_name != from_user:
                self._send(
                    client_socket=_socket,
                    message=message
                )
                
    def _recompute_shared(self) -> None:
        for current_name, client_socket in self.clients.items():
            print('Calculating shared for the: ', current_name)
            
            self._send(
                client_socket=client_socket,
                message=Message(
                    type=MessageType.UPDATE_KEY
                )
            )
            print(f'Sended update key to the {current_name}')
            
            response = self._read(client_socket=client_socket)
            print(f'Accepted response from the {current_name}')
            
            while response.type != MessageType.UPDATING_ENDED:
                self._send(
                    message=response,
                    client_socket=self.clients[response.content.toUser]
                )
                print(f'Sended compute to the {response.content.toUser}')
                
                responseComputed: Message = self._read(client_socket=self.clients[response.content.fromUser])
                print(f'Received computed from the {response.content.fromUser}')
                self._send(
                    message=responseComputed,
                    client_socket=self.clients[response.content.fromUser]
                )
                print(f'Sended computed to the {current_name}')
                
                response = self._read(client_socket=client_socket)
                print(f'Received another compute or key updates')
        
    def serve_client(self, client_socket: socket.socket) -> None:
        # We sending p and q along with the clients on the server
        response: Message = self._send(
            client_socket=client_socket,
            message=Message(
                type=MessageType.INITIAL_EXCHANGE,
                content=InitialExchangeContent(
                    p=self.p,
                    g=self.g,
                    clients=list(self.clients.keys())
                )
            ),
            receiving_types=[MessageType.STATUS_OK]
        )
        current_user_name: str = response.content.name
        print('Accepted a new connection: ', current_user_name)
        
        # Adding user to the activa clients
        self.clients[current_user_name] = client_socket
        
        # Notificating other users about new user
        self._notificate_all(
            from_user=current_user_name,
            message=Message(type=MessageType.USER_ADDITION, content=UserAdditionContent(user=current_user_name))
        )
        print('Notificated about new users!')
        
        # Recomputing all shared keys
        recalculating_thread = threading.Thread(
            target=self._recompute_shared
        )
        recalculating_thread.start()
        print('Computed shared number.')
        print()
        
        # Start accepting messages
        while True:
            request: Message = self._read(client_socket=client_socket)
            
            if request.type == MessageType.COMPUTE:
                response: Message = self._send(
                    message=request,
                    client_socket=self.clients[request.content.toUser],
                    receiving_types=[MessageType.COMPUTED]
                )
                _ = self._send(
                    message=response,
                    client_socket=client_socket
                )
                
            elif request.type == MessageType.COMPUTED:
                print('Alice recieved: ', request)
                self._send(
                    message=request,
                    client_socket=self.clients[request.content.toUser]
                )
            
            elif request.type == MessageType.UPDATING_ENDED:
                self._send(
                    message=request,
                    client_socket=client_socket
                )
    
    def serve_forever(self) -> None:
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.serve_client,
                args=(client_socket,)
            )
            client_thread.start()
            