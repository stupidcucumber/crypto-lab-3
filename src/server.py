import socket, threading, json
from .model import Message, MessageType, InitialExchangeContent, ClientsChangedContent


class Server:
    def __init__(self, port: int, p: int = 23, g: int = 11) -> None:
        self.socket: socket.socket = socket.create_server(('', port))
        self.clients_sockets: dict[str, socket.socket] = dict()
        self.clients: list[str] = []
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
    
    def _notificate_all(self, message: Message) -> None:
        for client_socket in self.clients_sockets.values():
            self._send(
                client_socket=client_socket,
                message=message
            )
        
    def serve_client(self, client_socket: socket.socket) -> None:
        # We sending p and q along with the clients on the server
        response: Message = self._send(
            client_socket=client_socket,
            message=Message(
                type=MessageType.INITIAL_EXCHANGE,
                content=InitialExchangeContent(
                    p=self.p,
                    g=self.g
                )
            ),
            receiving_types=[MessageType.STATUS_OK]
        )
        current_user_name: str = response.content.client
        print('Accepted a new connection: ', current_user_name)
        
        # Adding user to the activa clients
        self.clients_sockets[current_user_name] = client_socket
        self.clients.append(current_user_name)
        
        # Notificating other users about new user
        self._notificate_all(
            message=Message(
                type=MessageType.CLIENTS_CHANGED, 
                content=ClientsChangedContent(
                    p=self.p,
                    g=self.g,
                    clients=self.clients
                )
            )
        )
        
        # Start accepting messages
        while True:
            request: Message = self._read(client_socket=client_socket)
            print('From user: ', current_user_name, 'Request: ', request)
            
            if request.type == MessageType.COMPUTE:
                self._send(
                    message=request,
                    client_socket=self.clients_sockets[request.content.toUser]
                )
                
            elif request.type == MessageType.COMPUTED:
                self._send(
                    message=request,
                    client_socket=self.clients_sockets[request.content.toUser]
                )
            
            elif request.type == MessageType.UPDATE_KEY:
                self._send(
                    message=request,
                    client_socket=self.clients_sockets[request.content.toUser]
                )
    
    def serve_forever(self) -> None:
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.serve_client,
                args=(client_socket,)
            )
            client_thread.start()
            