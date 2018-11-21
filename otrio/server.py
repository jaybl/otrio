import socket
import sys
from threading import *
import pickle

def main(host, port):

    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.gethostname())
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    clients = []
    print("listening") 
    stop = True
    def clienthandler(c, name):
        clients.append(c)
        try:
            while True:
                data = c.recv(1024).decode("UTF-8")
                if not data:
                    break
                else:
                    #check if data recieved is game data or chat msg
                    if data == "begin_data_transfer_protocol:*~||":
                        data = c.recv(4096)
                        tags = pickle.loads(data)
                        for client in clients:
                            if client != c:
                                client.sendall(bytes("begin_data_transfer protocol:*~||".encode("UTF-8")))
                                client.send(data)
                    else:
                        for client in clients:
                            client.send(data.encode("UTF-8"))
        except Exception as e:
            print(e)
            clients.remove(c)
            '''
            for client in clients:
                client.send("{} has disconnected".format(name).encode("UTF-8"))
            '''
            c.close()

    while True:
        c, addr = s.accept()
        name = c.recv(1024).decode("UTF-8")
        print("accepted a client:", name)
        for client in clients:
            client.send("{} has joined".format(name).encode("UTF-8"))
        Thread(target=clienthandler, args=(c,name)).start()

if __name__ == '__main__':
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        main(host,port)
    except Exception as e:
        main('127.0.0.1',33000)
        
        
