import socket, time, os
from node import Node

class Client(Node):

    def __init__(self,hostname:str, server_port:int, name:str, my_port:int):
        super().__init__()
        self.__name = name
        self.__my_port = my_port
        self.__my_numbers = []
        self.__extra_numbers = []
        self.__missing_numbers = []
        self.__my_numbers_copy = []
        self.__connect_index_server(hostname,server_port)
    
    def __connect_index_server(self,hostname:str, server_port:int):
        res = self._make_request(
            hostname,
            server_port,
            '',
            {
                'name': self.__name,
                'port': self.__my_port
            }
        )

        self._node_list = res['nodes']
        self.__my_numbers = res['numbers']
        self.__my_numbers.sort()
        self.__my_numbers_copy = self.__my_numbers.copy()

        # Show info
        os.system('clear')
        self.__handle_numbers()

        print('-- FIRST CONNECT --')
        self._print_nodes()

        self.__start_to_listen()

# Mejor hacer con hilos actulizar nodos y otro para lo demas
    def __start_to_listen(self):
        client_socket = socket.socket()
        my_ip = socket.gethostbyname(socket.gethostname())
        client_socket.bind((my_ip,self.__my_port))
        client_socket.listen(2)
        while True:
            conn, address = client_socket.accept()
            waiting_info = self._receive_message(conn)

            if waiting_info['state'] == 'update':

                self._node_list = waiting_info['data']

                self.__show_info()
                print('-- NODE LIST UPDATE --')
                self._print_nodes()

            elif waiting_info['state'] == 'start':

                time.sleep(1)
                del self._node_list[my_ip]
                print('-- UPDATING CLIENTS --')
                self._update_all_clients(my_ip)
                conn.close()
                if self._node_list:
                    self.__resolve_numbers()
                else:
                    self.__show_info()
                break
            
            elif waiting_info['state'] == 'get_extra_numbers':
                data = self._create_message(self.__extra_numbers)
                conn.send(data)
            
            elif waiting_info['state'] == 'swap':
                get_numbers = waiting_info['data']['get_numbers']
                send_numbers = waiting_info['data']['send_numbers']
                for number_remove in get_numbers:
                    self.__extra_numbers.remove(number_remove)
                self.__extra_numbers.extend(send_numbers)
                self.__handle_numbers()
                self.__show_info()

                data = self._create_message({'state':'swapped'})
                conn.send(data)


            conn.close()
    
    def __resolve_numbers(self):
        while True:
            for client in self._node_list:
                res = self._make_request(
                    client,
                    self._node_list[client]['port'],
                    'get_extra_numbers',
                    None
                )
                numbers_checked = self.__check_numbers(res)
                if not numbers_checked:
                    continue
                
                print(f"Found this numbers : {numbers_checked} in client {(self._node_list[client]['name']).upper()}")
                time.sleep(10)

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
                
        
        self._stop_server()
          
    def __handle_numbers(self):
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
    
    def __check_numbers(self, numbers:list):
        numbers_checked = []
        for mn in self.__missing_numbers:
            if mn in numbers:
                numbers_checked.append(mn)
            
        return numbers_checked
    
    def __swap_numbers(self, hostname:str, port:int, get_numbers:list , send_numbers:list):
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

                    
    def __show_info(self):
        os.system('clear')
        print(f' ---- {self.__name.upper()} ---- ')
        print(f'My numbers : {self.__my_numbers_copy}')
        print(f'Missing numbers: {self.__missing_numbers}')
        print(f'Extra numbers: {self.__extra_numbers}')
        print(f'handle numbers: {self.__my_numbers}')


def main():
    print('---- CLIENT ---')
    name = input('My name : ')
    # name = 'Santiago'
    # my_port = int(input('my port: '))
    my_port = 5000
    hostname = input('Server ip: ')
    os.system('clear')
    client = Client(hostname, 5000, name, my_port)

if __name__ == '__main__':
    main()