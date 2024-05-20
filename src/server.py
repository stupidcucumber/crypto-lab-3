import socket, threading, json, time
from .model import Message, MessageType, InitialExchangeContent, UserAdditionContent


class Server:
    def __init__(self, port: int, p: int = 23, g: int = 11) -> None:
        self.socket: socket.socket = socket.create_server(('', port))
        self.clients: dict[str, socket.socket] = dict()
        self.p: int = p
        self.g: int = g
        
    def _read(self, client_socket: socket.socket) -> Message | None:
        message_raw = client_socket.recv(4096)
        message_str = message_raw.decode()
        print(message_str)
        message = Message(**json.loads(message_str))
        return message
    
    def _send(self, message: Message, client_socket: socket.socket, receiving_type: MessageType | None = None) -> Message | None:
        client_socket.send(message.model_dump_json().encode())
        if receiving_type is not None:
            response: Message = self._read(client_socket=client_socket)
            if response.type != receiving_type:
                raise ValueError('Status response is not OK. Received message: ', response)
            return response
    
    def _notificate_all(self, from_user: str, message: Message) -> None:
        for user_name, _socket in self.clients.items():
            if user_name != from_user:
                self._send(
                    client_socket=_socket,
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
                    g=self.g,
                    clients=list(self.clients.keys())
                )
            ),
            receiving_type=MessageType.STATUS_OK
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
        
        # Start accepting messages
        while True:
            request: Message = self._read(client_socket=client_socket)
            
            if request.type == MessageType.COMPUTE:
                response: Message = self._send(
                    message=request,
                    client_socket=self.clients[request.content.toUser],
                    receiving_type=MessageType.COMPUTED
                )
                _ = self._send(
                    message=response,
                    client_socket=client_socket,
                    receiving_type=MessageType.STATUS_OK
                )
    
    def serve_forever(self) -> None:
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.serve_client,
                args=(client_socket,)
            )
            client_thread.start()
            