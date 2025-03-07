import pickle, socket

class Node:
    HEADER_LENGTH = 10
    def __init__(self):
        self._node_list = {}

    def _create_message(self, data):
        data_serialized = pickle.dumps(data)
        data_length = str(len(data_serialized))
        # HEADER + Psayload
        message = bytes(f'{data_length:<{self.HEADER_LENGTH}}','utf-8') + data_serialized
        return message

    def _receive_message(self, current_socket:socket):
        data_length = current_socket.recv(self.HEADER_LENGTH)
        data_serialized = (bytes) (current_socket.recv(int(data_length)))
        data_deserialized = pickle.loads(data_serialized)
        return data_deserialized

    def _print_nodes(self):
        for node in self._node_list:
            print(f'{node} : {self._node_list[node]}')

    def _update_all_clients(self, current_node:str):
        for client in self._node_list:
            if current_node != client:
                broadcast_socket = socket.socket()
                broadcast_socket.connect((client, self._node_list[client]['port']))
                message = self._create_message({
                    'state':'update',
                    'data':self._node_list
                })
                broadcast_socket.send(message)
                broadcast_socket.close()
    
    def _make_request(self, hostname:str , port:int ,state:str, data):
        request_socket = socket.socket()
        request_socket.connect((hostname, port))
        message = self._create_message({
            'state':state,
            'data':data
        })
        request_socket.send(message)
        response = self._receive_message(request_socket)
        request_socket.close()
        return response

    def _stop_server(self):
        ips = list(self._node_list.keys())
        last_connection = socket.socket()
        last_connection.connect((ips[0], self._node_list[ips[0]]['port']))
        message = self._create_message({
            'state':'start',
        })
        last_connection.send(message)
        last_connection.close()
