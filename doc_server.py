import socket
import threading
import time


host = '127.0.0.1' 
port = 7890

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# keep record of clients, index : nickname,
# and last message to load existing text for new clients
clients = []
nicknames = {}
last_message = ''.encode()

# call function to send a message to all clients in client array
def broadcast(message, msg):
    global last_message
        
    for client in clients:
        client.send(message)

    # if msg is not a new client connection or disconnect record last message
    if msg:
        last_message = message


# thread function to handle individual client
def handle(client, index):
    global nicknames
    while True:
        # is message recieved broadcast to all clients
        try:
            message = client.recv(1024)
            broadcast(message, True)
        # if connection is lost remove from client list and nickname dict
        # tell all clients the clients index who left
        except:
            clients.remove(client)
            client.close()
            broadcast(f'{index}-DELCLIENT'.encode(), False)
            del nicknames[str(index)]
            print(nicknames)
            break


def recieve():
    global clients
    global nicknames
    global last_message

    while True:
        try:
            # accept all new connections and add to client list
            client, address = server.accept()
            print(client)
            clients.append(client)
            time.sleep(0.1)
            print(f'connected with {str(address)}')

            # send client its index in the client list
            # get nickname as repoonse, add to nickname dict 
            client.send(f'{len(clients)}-NICK'.encode())
            index, nickname = client.recv(1024).decode().split('-')
            nicknames[index] = nickname

            # loop over nicknames and broadcast each to the clients
            for ind, nn in nicknames.items():
                broadcast(f'{ind}-{nn}-NEWCLIENT'.encode(), False)
                time.sleep(0.01)

            # populate new clients with existing text    
            broadcast(last_message, True)
            
            # each new client will have a thread to handle all its actions
            threading.Thread(target=handle, args=(client,index,)).start()
            
        except Exception as e:
            print(e)


        

print('server is listening')
recieve()