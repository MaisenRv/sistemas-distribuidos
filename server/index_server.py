import random, socket, os
from core.node import Node

class IndexServer(Node):

    def __init__(self, port:int ,client_number:int) -> None:
        super().__init__()
        # server Info
        self.__my_hostname = socket.gethostbyname(socket.gethostname())
        self.__my_port = port
        self.__client_number = client_number


        self.__current_node = ''
        self.__numbers = self.__generate_numbers(client_number)
        
    def start(self):
        self.__register(self.__my_hostname ,self.__my_port,self.__client_number)

    def __register(self,hostname:str, port:int, client_number:int) -> None:
        #start server
        server_socket = socket.socket()
        server_socket.bind((hostname,port))
        server_socket.listen(client_number)
        print(f'Start numbers : {self.__numbers}')
        while True:
            conn,address = server_socket.accept()
            info_client = self._receive(conn)
            # Add new node 
            self._node_list[address[0]] = {
                'name':info_client['data']['name'],
                'port':info_client['data']['port'],
                'completed':False
            }
            # Update current node
            self.__current_node = address[0]
            self._send(
                conn,
                '',
                {
                    'nodes':self._node_list, 
                    'numbers': self.__get_selected_numbers(),
                    'max_clients':client_number
                }
            )

            # Show info
            os.system('clear')
            print(f'Remaining numbers : {self.__numbers}')
            print('--- NODES NOW ---')
            self._print_nodes()
            conn.close()
            self._send_all_nodes(self.__current_node,'update',{'nodes':self._node_list})
            if not self.__numbers:
                break
        server_socket.close()
    

    def __generate_numbers(self,client_number:int) -> list:
        numbers = []
        for i in range(client_number):
            for j in range(11):
                numbers.append(j)
        random.shuffle(numbers)
        return numbers

    def __get_selected_numbers(self) -> list:
        selected_numbers = []
        for i in range(11):
            selected_numbers.append(self.__numbers.pop())
            #random.shuffle(self.__numbers)
        return selected_numbers
