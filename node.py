import socket
from message import Message

class Node:
    HEADER_LENGTH = 10
    def __init__(self):
        self._node_list = {}
    
    def _receive(self, conn:socket) -> dict:
        return Message.receive_message(self.HEADER_LENGTH, conn)
    
    def _send(self, conn:socket, state:str, data:dict) -> None:
        message = Message.create_message(self.HEADER_LENGTH, state, data)
        conn.send(message)

    def _print_nodes(self):
        for node in self._node_list:
            print(f'{node} : {self._node_list[node]}')
    
    def _make_request(self, hostname:str , port:int ,state:str, data:dict) -> dict:
        request_socket = socket.socket()
        request_socket.connect((hostname, port))
        self._send(request_socket,state,data)
        response = self._receive(request_socket)
        request_socket.close()
        return response
    
    def _send_all_nodes(self, current_node:str, state:str, data:dict):
        for client in self._node_list:
            if current_node != client and self._node_list[client]['completed'] == False:
                broadcast_socket = socket.socket()
                broadcast_socket.connect((client, self._node_list[client]['port']))
                self._send(broadcast_socket, state, data)
                broadcast_socket.close()
    

    def _stop(self):
        for client in self._node_list:
            if not self._node_list[client]['completed']:
                last_connection = socket.socket()
                last_connection.connect((client, self._node_list[client]['port']))
                self._send(last_connection,'start',{})
                last_connection.close()
                return
