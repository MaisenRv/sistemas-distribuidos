import argparse, os
from client.client import Client
from server.index_server import IndexServer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=str , help='"server" or "client"', default='')
    parser.add_argument('-p', type=int , help='Clinet\'s port, default 5000', default=5000)
    parser.add_argument('-n', type=int , help='Number of clients, default 5', default=5)
    args = parser.parse_args()
    
    if args.t == 'server':
        os.system('clear')
        i_server = IndexServer(5000,args.n)
        i_server.start()
    elif args.t == 'client':
        os.system('clear')
        print('---- CLIENT ---')
        hostname = input('Server ip: ')
        client = Client(args.p,hostname,5000)
        client.start()
    else:
        print(f'Type "{args.t}" not found')


if __name__ == '__main__':
    main()
