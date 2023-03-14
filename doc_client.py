import socket
import threading
from tkinter import *
import os
import time

nickname = input('Nickname: ')

# connect to server
host = '127.0.0.1' 
port = 7890
cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cl.connect((host, port))

# global 
gui = None

# thread function handles tkinter object and sending messages
def get_editor():
    global gui
    
    root = Tk()
    gui = Window(root)
    gui.root.mainloop()

    os._exit(1)


# main gui window
class Window:

    cols = ['red' , 'green' , 'blue' , 'cyan' , 'yellow' , 'magenta']

    def __init__(self, root) -> None:
        # establish window
        self.root = root
        self.root.geometry('600x500')
        self.root.title('notepad')

        # creat text box
        self.textbox = Text(root)
        self.textbox.grid(row=0, column=0)
        self.textbox.bind("<Key>", lambda event: self.reset_modifier(event))

        #configuring a tag called start
        self.textbox.tag_configure('red', foreground='red')
        self.textbox.tag_configure('green', foreground='green')
        self.textbox.tag_configure('blue', foreground='blue')
        self.textbox.tag_configure('cyan', foreground='cyan')
        self.textbox.tag_configure('yellow', foreground='yellow')
        self.textbox.tag_configure('magenta', foreground='magenta')

        # set client index for color and record all nicknames
        self.client_index = 0
        self.nicknames = []

    # after each keystroke, send server all information
    def reset_modifier(self, event):
        r,c = self.textbox.index('insert').split('.')
        text = self.textbox.get('1.0', 'end-1c')
        client_index = self.client_index
        text = f'{client_index}-{nickname}-{text + event.char}-{r}-{c}'
        cl.send(text.encode())

    # when message is recieved delete textbox, update with new message
    # add text color to changes - based on client index who sent message
    def write_to_textbox(self, ind, msg, r, c):   
        self.textbox.delete('1.0', 'end-1c')
        pos1 = f'{r}.{c}'
        pos2 = f'{r}.{int(c)+1}'
        self.textbox.insert('1.0', msg)
        self.textbox.tag_add(self.cols[int(ind)], pos1, pos2)
    
    # set own client index to send when changing document
    def set_client_index(self, ind):
        self.client_index = int(ind)
    
    # when new user joins add label 
    def add_user_label(self, user_ind, nick):
        new_button = True

        for nn in self.nicknames:
            if nn == nick:
                new_button = False
        
        if new_button:
            # create button, link it to clickExitButton()
            self.exitButton = Button(self.root, text=nick, bg=self.cols[int(user_ind)])
            # place button at (0,0)
            self.exitButton.grid(row=0, column=user_ind, columnspan=1, sticky=N+W)
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)
            self.nicknames.append(nick)

    # when user leaves delete button
    def rem_user_label(self, ind):
        widget = self.root.grid_slaves(row=0, column=ind)[0]
        widget.grid_forget()
        

# thread function that handles all recieved messages from server
def recieve():

    while True:
        try:

            message = cl.recv(1024).decode()

            # if message rec ends in 'NICK' record index #, send nickname
            if message[-4:] == 'NICK':
                cl_in,NICK = message.split('-')
                client_index = cl_in
                gui.set_client_index(client_index)
                cl.send(f'{client_index}-{nickname}'.encode())

            # if message rec ends in 'NEWCLIENT', add new button to window
            elif message[-9:] == 'NEWCLIENT':
                msg = message.split('-')
                gui.add_user_label(msg[0], msg[1])

            # if message rec ends in 'DELCLIENT', remove button from window
            elif message[-9:] == 'DELCLIENT':
                msg = message.split('-')
                gui.rem_user_label(msg[0])

            # if message is a change in the textbox
            else:
                message = message.split('-')
                try:
                    # if message is not from the current client updat textbox
                    if message[1] != nickname:
                        gui.write_to_textbox(message[0],message[2], message[3], message[4])
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)


# start threads
threading.Thread(target=get_editor).start()
time.sleep(0.5)
threading.Thread(target=recieve).start()
