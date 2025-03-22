import argparse, os
from client.client import Client
from server.index_server import IndexServer

def main():
    parser = argparse.ArgumentParser(description='Arguments: ')
    parser.add_argument('--type', type=str , help='Server or client', default='')
    args = parser.parse_args()
    
    if args.type == 'server':
        os.system('clear')
        i_server = IndexServer(5000,3)
        i_server.start()
    if args.type == 'client':
        os.system('clear')
        print('---- CLIENT ---')
        hostname = input('Server ip: ')
        client = Client(hostname,5000)
        client.start()


if __name__ == '__main__':
    main()