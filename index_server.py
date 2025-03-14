import random, socket, os
from node import Node

class IndexServer(Node):

    def __init__(self, hostname:str, port:int ,client_number:int):
        super().__init__()
        self.__current_node = ''
        self.__numbers = self.__generate_numbers(client_number)
        self.__register(hostname,port,client_number)
        
    def __register(self,hostname:str, port:int, client_number:int):
        #start server
        server_socket = socket.socket()
        server_socket.bind((hostname,port))
        server_socket.listen(client_number)
        print(f'Start numbers : {self.__numbers}')
        while True:
            conn,address = server_socket.accept()

            # Deserialized data
            info_client = self._receive_message(conn)
            
            # Add new node 
            self._node_list[address[0]] = info_client['data']
            # Update current node
            self.__current_node = address[0]

            info_to_send = {
                'nodes':self._node_list,
                'numbers': self.__get_selected_numbers()
            }
            conn.send(self._create_message(info_to_send))

            # Show info
            os.system('clear')
            print(f'Remaining numbers : {self.__numbers}')
            print('--- NODES NOW ---')
            self._print_nodes()

            conn.close()
            
            self._update_all_clients(self.__current_node)
            if not self.__numbers:
                self._stop_server()
                break
       
    def __generate_numbers(self,client_number:int):
        numbers = []
        for i in range(client_number):
            for j in range(11):
                numbers.append(j)
        random.shuffle(numbers)
        return numbers

    def __get_selected_numbers(self):
        selected_numbers = []
        for i in range(11):
            selected_numbers.append(self.__numbers.pop())
            #random.shuffle(self.__numbers)
        return selected_numbers



def main():
    ip = socket.gethostbyname(socket.gethostname())
    server = IndexServer(ip,5000,5)

if __name__ == '__main__':
    main()