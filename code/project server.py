# Dvir Sadon
import socket
import select
import re
import cPickle as pickle
import hashlib
from project import make_pickle
import os
import struct

PORT = 8389

myusers = make_pickle.Pickfile("users.pickle")
myusers.create_file({})
users = myusers.get_value()  # List of all users registered (Non workers)

messages_to_send = []  # List of awayting messages

ourips = make_pickle.Pickfile("ourip.pickle")
ourips.create_file({"12": "12", "1234": "1234"})
ourip = ourips.get_value()  # Dict of worker Username:Password

noconnectew = []  # List of sockets for free workers

onlineu = {}  # Dict of Name:Socket for all the online clients (No workers)

links = []  # List of lists - in r[0] the client socket and in r[1] the worker socket


def send_me():
    """Sends the awayting messages to the right client"""
    for message in messages_to_send:
        (client_socket1, data) = message
        for p in links:
            if client_socket1 is p[0]:
                print data
                p[1].send(data)
                break
            elif client_socket1 is p[1]:
                p[0].send(data)
                break
        messages_to_send.remove(message)


def recving():
    """Listens to clients, recieves messages and redirects to the right func for login or sighn up """
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(10)
    global open_client_sockets
    open_client_sockets = []
    saver = {}
    while True:
        rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
        global current_socket
        for current_socket in rlist:
            if current_socket is server_socket:  # If is done and list is empty
                (new_socket, address) = server_socket.accept()
                open_client_sockets.append(new_socket)
                saver[new_socket] = address
            else:
                global data
                data = current_socket.recv(1024)
                print "got data = "+str(data)
                if data == "^"or data == "~":
                    while not noconnectew:  # wait till a worker is free
                        pass
                    sok = noconnectew[0]
                    noconnectew.remove(sok)
                    links.append([current_socket, sok])  # [Client, Worker]
                    if data == "~":
                        video_chat(sok, current_socket)
                elif data.startswith("@"):  # If trying to log in
                    is_user_valid()
                elif data.startswith("`"):  # If trying to register
                    register()
                elif data == "<":
                    quit_chat(current_socket)
                elif data == "":  # if logging out
                    logout()
                    print "Connection with client closed"
                else:
                    messages_to_send.append((current_socket, data))
        send_me()


def quit_chat(sock):
    for q in links:
        if q[0] is sock:
            q[1].send("The client hs left the chat, Wait for another one to send a message")
            noconnectew.append(q[1])
            links.remove(q)
            break


def video_chat(sok, new_socket):
    """creates the network between the two clients"""
    sok.send("~")
    new_socket.send(str(sok.getsockname()[0]))


def register():
    """Handles the register requests"""
    leng = current_socket.recv(4)
    got = current_socket.recv(int(leng))
    global image
    image = ""
    while not got.endswith("done"):
        image += got
        leng = current_socket.recv(4)

        got = current_socket.recv(int(leng))
    if image.endswith("done"):
        image = image[:len(image)-4]

    if not str(image) == '':
        global filename1
        filename1 = current_socket.recv(1024)
    else:
        image = ''
    reguser = str(re.search("`(.*)#(.*)", data).group(1))
    regpass = str(re.search("`(.*)#(.*)", data).group(2))
    client_list = myusers.get_value()
    worker_dict = ourips.get_value()
    if reguser not in client_list.keys() and reguser not in worker_dict.keys():  # New account
        users[reguser] = regpass
        pick = myusers.open_file('wb')
        pickle.dump(users, pick, protocol=pickle.HIGHEST_PROTOCOL)
        pick.close()
        if not str(image) == '':
            savefiles(reguser)
        current_socket.send("!")
    else:
        current_socket.send("?")


def savefiles(name):
    """creates folder and saves the file"""
    os.makedirs(name)
    pathing = os.getcwd()+r"\\"+name+r"\\"+filename1
    if image is not '':
        medfile = open(pathing, 'wb')
        medfile.write(image)


def logout():
    """Handles the logout requests"""
    for r in links:
        if r[0] is current_socket:
            current_socket.send(";")
            for wt in onlineu.keys():
                if onlineu[wt] is current_socket:
                    del onlineu[wt]
            links.remove(r)
    open_client_sockets.remove(current_socket)


def is_user_valid():
    """Handles the sign in requests by checking if the user is saved"""
    username = str(re.search("@(.*)#(.*)", data).group(1))
    password = str(re.search("@(.*)#(.*)", data).group(2))
    if username in ourip.keys() and password == hashlib.sha256(ourip[username]).hexdigest():  # If saved as employee
        noconnectew.append(current_socket)
        current_socket.send('200')
    else:
        try:
            if users[username] == password:
                current_socket.send("200")  # Send confirmation
                onlineu[username] = current_socket
        except Exception:
            current_socket.send("404")


recving()
