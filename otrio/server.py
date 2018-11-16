from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

clients = {}
addresses = {}
HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        if len(addresses) <= 4: #trying to limit number of ppl to the playercount
            client, client_address = SERVER.accept()
            print("%s:%s has connected." % client_address)
            client.send(bytes("Connection successful. Enter your name:\n", "utf8"))
            addresses[client] = client_address
            Thread(target=handle_client, args=(client,)).start()

def count_samename(name: str):
    names = list(clients.values())
    return names.count(name)

def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    clients[client] = name
    count = ''
    if count_samename(name) > 1:
        count = str(count_samename(name))
    msg = "{0}({1}) has joined the chat!".format(name ,count)
    broadcast(bytes(msg, "utf8"))
    while True:
        msg = client.recv(BUFSIZ)
        m = msg.decode("utf-8")
        print(name + ": " + m)
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            print("%s has left the chat." % name)
            break

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

if __name__ == "__main__":
    SERVER.listen(5)  # Listens for 5 connections at max.
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SERVER.close()
