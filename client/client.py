import socket, time, os
from core.node import Node

class Client(Node):

    def __init__(self,client_port:int ,server_hostname:str, server_port:int) -> None:
        super().__init__()
        # client info
        self.__name = input('My name : ')
        self.__my_port = client_port
        self.__my_ip = socket.gethostbyname(socket.gethostname())
        self.__my_numbers = []
        self.__extra_numbers = []
        self.__missing_numbers = []
        self.__my_numbers_copy = []
        self.__max_clients = 0
        # server info
        self.__server_info = {'hostname':server_hostname, 'port':server_port}

    def start(self) -> None:
        self.__connect_index_server()

        if len(self._node_list) < self.__max_clients:
            self.__update_list()

        ips = list(self._node_list.keys())
        if ips[0] != self.__my_ip:
            self.__listen()
            return
        time.sleep(2)
        self.__resolve_numbers()

    def __connect_index_server(self) -> None:
        res = self._make_request(
            self.__server_info['hostname'],
            self.__server_info['port'],
            '',
            {
                'name': self.__name,
                'port': self.__my_port
            } 
        )

        self._node_list = res['data']['nodes']
        self.__my_numbers = res['data']['numbers']
        self.__max_clients = res['data']['max_clients']
        self.__my_numbers.sort()
        self.__my_numbers_copy = self.__my_numbers.copy()

        # Show info
        os.system('clear')
        self.__handle_numbers()
        print('-- FIRST CONNECT --')
        self._print_nodes()

    def __update_list(self) -> None:
        client_socket = socket.socket()
        client_socket.bind((self.__my_ip,self.__my_port))
        client_socket.listen(2)
        while True:
            conn, address = client_socket.accept()
            info = self._receive(conn)
            
            if info['state'] == 'update':
                self._node_list = info['data']['nodes']
                self.__show_info()
                print('-- NODE LIST UPDATE --')
                self._print_nodes()
                conn.close()
            if len(self._node_list) == self.__max_clients:
                conn.close()
                break
        client_socket.close()


    def __listen(self) -> None:
        client_socket = socket.socket()
        client_socket.bind((self.__my_ip,self.__my_port))
        client_socket.listen(2)
        while True:
            conn, address = client_socket.accept()
            waiting_info = self._receive(conn)

            if waiting_info['state'] == 'get_extra_numbers':
                self._send(conn,'',{'extra_numbers':self.__extra_numbers})
            
            elif waiting_info['state'] == 'swap':
                get_numbers = waiting_info['data']['get_numbers']
                send_numbers = waiting_info['data']['send_numbers']
                for number_remove in get_numbers:
                    self.__extra_numbers.remove(number_remove)
                self.__extra_numbers.extend(send_numbers)
                self.__handle_numbers()
                self.__show_info()
                self._send(conn,'swapped',{})
            
            elif waiting_info['state'] == 'completed_node':
                self._node_list[waiting_info['data']['node']]['completed'] = True
                os.system('clear')
                self.__show_info()
                self._print_nodes()

            elif waiting_info['state'] == 'start':
                ips = list(self._node_list.keys())
                if ips[-1] != self.__my_ip:
                    self.__resolve_numbers()
                break
            conn.close()
        client_socket.close()
    
    def __resolve_numbers(self) -> None:
        for client in self._node_list:
            if (client == self.__my_ip) or (self._node_list[client]['completed'] == True):
                continue
            
            res = self._make_request(
                client,
                self._node_list[client]['port'],
                'get_extra_numbers',
                {}
            )

            numbers_checked = self.__check_numbers(res['data']['extra_numbers'])
            if not numbers_checked:
                continue
            
            print(f"Found this numbers : {numbers_checked} in client {(self._node_list[client]['name']).upper()}")
            time.sleep(5)

            swap_numbers = []
            numbers_checked_copy = numbers_checked.copy()

            if len(numbers_checked) > len(self.__extra_numbers):
                numbers_checked.clear()
                for i in range(len(self.__extra_numbers)):
                    swap_numbers.append(self.__extra_numbers[i])
                    numbers_checked.append(numbers_checked_copy[i])
                    numbers_checked_copy.remove(numbers_checked[i])

                self.__swap_numbers(client,self._node_list[client]['port'],numbers_checked,swap_numbers)
                time.sleep(1)
                if not self.__extra_numbers and self.__missing_numbers:
                    self.__swap_numbers(client,self._node_list[client]['port'],numbers_checked_copy,[])
                    time.sleep(1)


            if len(numbers_checked) <= len(self.__extra_numbers):
                for i in range(len(numbers_checked)):
                    swap_numbers.append(self.__extra_numbers[i])
                self.__swap_numbers(client,self._node_list[client]['port'],numbers_checked,swap_numbers)
                time.sleep(1)

            if not self.__missing_numbers and self.__extra_numbers:
                self.__swap_numbers(client,self._node_list[client]['port'],[],self.__extra_numbers)
            
            if not self.__extra_numbers and not self.__missing_numbers:
                break
        self._node_list[self.__my_ip]['completed'] = True
        self._send_all_nodes(self.__my_ip,'completed_node',{'node':self.__my_ip})
        self._stop()

    def __handle_numbers(self) -> None:
        self.__my_numbers.extend(self.__extra_numbers)
        self.__extra_numbers.clear()
        self.__missing_numbers.clear()
        for i in range(len(self.__my_numbers)):
            times_repeated = self.__my_numbers.count(i)
            if times_repeated == 0:
                self.__missing_numbers.append(i)
            elif times_repeated > 1:
                for j in range(times_repeated - 1):
                    self.__extra_numbers.append(i)
                    self.__my_numbers.remove(i)
        self.__my_numbers.sort()
        self.__show_info()
    
    def __check_numbers(self, numbers:list) -> list:
        numbers_checked = []
        for mn in self.__missing_numbers:
            if mn in numbers:
                numbers_checked.append(mn)
        return numbers_checked
    
    def __swap_numbers(self, hostname:str, port:int, get_numbers:list , send_numbers:list) -> None:
        res = self._make_request(
            hostname,
            port,
            'swap',
            {
                'get_numbers':get_numbers,
                'send_numbers':send_numbers
            }
        )

        if res['state'] == 'swapped':
            for number_remove in send_numbers:
                    self.__extra_numbers.remove(number_remove)
            self.__extra_numbers.extend(get_numbers)
            self.__handle_numbers()
            self.__show_info()


                    
    def __show_info(self) -> None:
        os.system('clear')
        print(f' ---- {self.__name.upper()} ---- ')
        print(f'My numbers : {self.__my_numbers_copy}')
        print(f'Missing numbers: {self.__missing_numbers}')
        print(f'Extra numbers: {self.__extra_numbers}')
        print(f'handle numbers: {self.__my_numbers}')

