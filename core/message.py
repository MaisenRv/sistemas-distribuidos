import pickle, socket

class Message:

    @staticmethod
    def create_message(header_length:int, state:str, data:dict) -> bytes:
        formated_data = Message.format_message(state,data)
        return Message.serialized_data(header_length,formated_data)
    
    @staticmethod
    def format_message(state: str, data:dict) -> dict:
        message = { 'state':state, 'data':data }
        return message

    @staticmethod
    def serialized_data(header_length:int, data:dict) -> bytes:
        data_serialized = pickle.dumps(data)
        data_length = str(len(data_serialized))
        # HEADER + Psayload
        message = bytes(f'{data_length:<{header_length}}','utf-8') + data_serialized
        return message
    
    @staticmethod
    def receive_message(header_length:int ,current_socket:socket) -> dict:
        data_length = current_socket.recv(header_length)
        data_serialized = (bytes) (current_socket.recv(int(data_length)))
        data_deserialized = pickle.loads(data_serialized)
        return data_deserialized