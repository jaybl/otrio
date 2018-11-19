import socket
from threading import *


def main(host='127.0.0.1', port=33000):

    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    clients = []
    print("listening")

    def clienthandler(c, name):
        clients.append(c)
        try:
            while True:
                data = c.recv(1024).decode("UTF-8")
                if not data:
                    break
                else:
                    print(data)
                    for client in clients:
                        client.send(data.encode("UTF-8"))
        except:
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
    main()
