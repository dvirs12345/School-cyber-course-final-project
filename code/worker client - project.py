# Dvir Sadon
import socket
import threading
import hashlib
import struct
import pickle
import cv2
import Tkinter as tk
from Tkinter import *

PORT = 8389
TITLE_FONT = ("Comic Sans MS", 40)


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('1000x600')
        tk.Tk.iconbitmap(self, default='deaf.ico')
        tk.Tk.wm_title(self, "DPR")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ChatPage, LogIn):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LogIn)

    def show_frame(self, cont):
        """the function gets a frame and displays it"""
        frame = self.frames[cont]
        frame.tkraise()

    def destroy_frame(self):
        """the function stops the program"""
        self.destroy()


def login():
    """handles the login protocol"""
    global client_socket
    client_socket = socket.socket()
    client_socket.connect(('127.0.0.1', PORT))
    app = App()
    app.mainloop()
    mamain()


def pgot():
    """recieves from the server"""
    got = " "
    while not got == '':
        got = client_socket.recv(1024)
        if got == "~":
            video_recv()
        if got == ";":
            mamain()
        operate_chat(got)
    client_socket.close()


def video_recv():
    """turns this into a server and gets the video live"""
    client_socket.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 8380))
    s.listen(10)
    conn, addr = s.accept()

    data = ""
    payload_size = struct.calcsize("L")
    while True:
        while len(data) < payload_size:
            data += conn.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    client_socket.close()
    cv2.destroyAllWindows()


def mamain():
    """handles the chat"""
    # hashpass = hashlib.sha256(password).hexdigest()
    # client_socket.send("@" + username + "#" + hashpass)
    first_gotten = ""
    while first_gotten == "":
        first_gotten = client_socket.recv(1024)
        if first_gotten == "~":
            video_recv()
        if first_gotten == ";":
            mamain()
    print first_gotten
    operate_chat(first_gotten)
    print "activate"
    recvth = threading.Thread(target=pgot)
    recvth.start()
    while True:
        answer = raw_input('Your answer: ')
        client_socket.send(name + " :" + answer)


class LogIn(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        login_label = tk.Label(self, text="Log In", font=TITLE_FONT, height=2)
        login_label.pack(pady=10, padx=10)
        username_controller = tk.Frame(self, self)
        username_controller.pack()
        username_label = tk.Label(username_controller, text="Username:")
        username_label.pack(side=tk.LEFT, pady=(20, 5))
        self.u_entry = Entry(username_controller, width=22)
        self.u_entry.pack(side=tk.RIGHT, pady=(20, 5))
        password_controller = tk.Frame(self, self)
        password_controller.pack()
        password_label = tk.Label(password_controller, text=" Password:")
        password_label.pack(side=tk.LEFT, pady=(10, 20))
        self.p_entry = Entry(password_controller, width=22, show='*')
        self.p_entry.pack(side=tk.RIGHT, pady=(10, 20))
        r_button = tk.Button(self, text="Log In", height=3, width=30, command=lambda: self.whenlogin(controller))
        r_button.pack(pady=(10, 10))
        quit_button = tk.Button(self, text="Quit",
                                command=lambda: controller.destroy_frame(), height=3, width=30)
        quit_button.pack(anchor='center', pady=(20, 20))

    def whenlogin(self, controller):
        """Handles the login protocol"""
        got = self.u_entry.get()
        got2 = self.p_entry.get()
        if str(got).startswith("`"):
            got = got[1::]

        if not got == "" or not got2 == "":
            global name
            name = got
            hashgot2 = hashlib.sha256(got2).hexdigest()
            client_socket.send('@' + str(got) + '#' + str(hashgot2))
            print 'waiting'
            confirmation = str(client_socket.recv(1024))
            print confirmation
            if confirmation == "200":
                controller.show_frame(ChatPage)
                mainthread = threading.Thread(target=mamain)
                mainthread.start()
            else:
                error_lable = tk.Label(self, fg='red', text="invalid password or username")
                error_lable.pack(padx=5, pady=5)


class ChatPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        scrollb = Scrollbar(self)
        scrollb.pack(side="left", fill="y", expand=FALSE)
        new_lable = Label(self, text="Chat", font=TITLE_FONT)
        new_lable.pack(pady=10, padx=10)
        global Texts
        Texts = Text(self, height=20, width=40)
        Texts.pack(anchor="center", pady=20)
        Texts.configure(state="disabled")
        message_controller = tk.Frame(self, self)
        message_controller.pack()
        send_button = Button(message_controller, text="  Send  ", width=7, command=self.trial)
        send_button.pack(side=tk.LEFT, padx=5)
        self.my_entry = Entry(message_controller, width=42)
        self.my_entry.pack(side=tk.RIGHT)
        scrollb = Scrollbar(self)
        scrollb.config(command=Texts.yview)
        Texts.config(yscrollcommand=scrollb.set)
        # scrollb.pack(side="left", fill="y", expand=FALSE)

    def trial(self):
        """Sends the messages and updates it on the client's screen"""
        client_socket.send(name + " " + self.my_entry.get())
        print "sent"
        Texts.configure(state="normal")
        my_text = "YOU: " + self.my_entry.get() + "\n"
        Texts.insert(END, my_text)
        Texts.configure(state="disabled")


def operate_chat(got_data):
    """operates the chat - opens and closes the Text and recieves info"""
    if not got_data == '~':
        got_data += "\n"
        Texts.configure(state="normal")
        Texts.insert(END, got_data)
        Texts.configure(state="disabled")


login()
