# Dvir Sadon
from Tkinter import *
import Tkinter as tk
import socket
import threading
import hashlib
import tkFileDialog
import os
import struct
import cv2
import pickle
import time

PORT = 8389
LABELX = 0.2
myfont = ("Calibri", 20)
TITLE_FONT = ("Comic Sans MS", 40)

name = ""


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
        for F in (MainMenu, ChatPage, RegisterPage, LogIn):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LogIn)

    def show_frame(self, cont):
        """the function gets a frame and displays it"""
        frame = self.frames[cont]
        frame.tkraise()
        if cont is ChatPage:
            chatcon()

    def destroy_frame(self):
        """the function stops the program"""
        self.destroy()


class Client:
    def __init__(self):
        self.client_socket = socket.socket()
        self.client_socket.connect(('127.0.0.1', PORT))

    def get_socket(self):
        """Returns the socket"""
        return self.client_socket

    def close_socket(self):
        """Closes the socket"""
        self.client_socket.close()


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
        register_button = tk.Button(self, text="Register",
                            command=lambda: controller.show_frame(RegisterPage), height=3, width=30)
        register_button.pack(anchor='center', pady=(20, 20))
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
            client.get_socket().send('@' + str(got) + '#' + str(hashgot2))
            confirmation = str(client.get_socket().recv(1024))
            print confirmation
            if confirmation == "200":
                controller.show_frame(MainMenu)
            else:
                error_lable = tk.Label(self, fg='red', text="invalid password or username")
                error_lable.pack(padx=5, pady=5)


class MainMenu(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        chat_controller = tk.Frame(self, self)
        chat_controller.pack()
        chatlink = Button(chat_controller, command=lambda: controller.show_frame(ChatPage),
                          text=" enter a chat ")  # command to the chat page
        chatlink.pack(side=tk.LEFT, pady=10, padx=10)
        videolink = Button(chat_controller, text=" enter a video chat ", command=lambda: videochat(controller))
        videolink.pack(side=tk.RIGHT, pady=(20, 20))
        top_controller = tk.Frame(self, self)
        top_controller.pack()

        self.firephoto = PhotoImage(file="Fire2.gif")
        firebutton = Button(top_controller, height=250, width=250, command=lambda: emergency(controller, "FIRE"))
        firebutton.config(image=self.firephoto)
        firebutton.pack(side=tk.LEFT, pady=5, padx=25)
        self.robbphoto = PhotoImage(file="Robbery2.gif")
        robbbutton = Button(top_controller, image=self.robbphoto, height=250, width=250
                          , command=lambda: emergency(controller, "ROBBERY"))
        robbbutton.pack(side=tk.RIGHT, pady=5)
        bottom_controller = tk.Frame(self, self)
        bottom_controller.pack()
        self.healthphoto = PhotoImage(file="Redcross2.gif")
        healhbutton = Button(bottom_controller, image=self.healthphoto, height=250, width=250
                             , command=lambda: emergency(controller, "MEDICAL"))
        healhbutton.pack(side=tk.LEFT, pady=5, padx=25)
        self.gasphoto = PhotoImage(file="1Gas_Leak.gif")
        gassbutton = Button(bottom_controller, image=self.gasphoto, height=250, width=250
                          , command=lambda: emergency(controller, "GAS LEAK"))
        gassbutton.pack(side=tk.RIGHT, pady=5)


def emergency(controller, eme):
    controller.show_frame(ChatPage)
    client.client_socket.send(eme)


def videochat(controller):
    """Not finnished yet"""
    client.client_socket.send("~")
    controller.destroy_frame()
    # chat_thread = threading.Thread(target=lambda: controller.show_frame(ChatPage))
    # chat_thread.start()
    newip = client.client_socket.recv(1024)
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((newip, 8380))
    cap = cv2.VideoCapture(0)
    time.sleep(1)
    while True:
        ret, frame = cap.read()
        data = pickle.dumps(frame)
        clientsocket.sendall(struct.pack("L", len(data)) + data)
    client.client_socket.close()
    cv2.destroyAllWindows()


def chatcon():
    """when connecting to the chat segment"""
    client.get_socket().send("^")
    print "Connected"
    operate_thread = threading.Thread(target=operate_chat)
    operate_thread.start()


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
        quit_button = Button(self, text="  Quit  ", command=lambda: self.quit_chat(controller))
        quit_button.pack(pady=30, padx=10)
        # scrollb.pack(side="left", fill="y", expand=FALSE)

    def quit_chat(self, controller):
        client.client_socket.send("<")
        controller.show_frame(MainMenu)

    def trial(self):
        """Sends the messages and updates it on the client's screen"""
        client.get_socket().send(name + " " + self.my_entry.get())
        print "sent"
        Texts.configure(state="normal")
        my_text = "YOU: " + self.my_entry.get() + "\n"
        Texts.insert(END, my_text)
        Texts.configure(state="disabled")


def operate_chat():
    """operates the chat - opens and closes the Text and recieves info"""
    while True:
        got_data = client.get_socket().recv(1024)
        got_data += "\n"
        Texts.configure(state="normal")
        Texts.insert(END, got_data)
        Texts.configure(state="disabled")


class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        register_label = tk.Label(self, text="Register", font=TITLE_FONT, height=2)
        register_label.pack(pady=10, padx=10)

        username_controller = tk.Frame(self, self)
        username_controller.pack()
        username_label = tk.Label(username_controller, text="Username:")
        username_label.pack(side=tk.LEFT, pady=10)
        self.u_entry = Entry(username_controller, width=22)
        self.u_entry.pack(side=tk.RIGHT, pady=10)

        password_controller = tk.Frame(self, self)
        password_controller.pack()
        password_label = tk.Label(password_controller, text=" Password:")
        password_label.pack(side=tk.LEFT, pady=10)
        self.p_entry = Entry(password_controller, width=22, show='*')
        self.p_entry.pack(side=tk.RIGHT, pady=10)

        file_controller = tk.Frame(self, self)
        file_controller.pack()
        select_label = tk.Label(file_controller, text=" select a medical file ->")
        select_label.pack(side=tk.LEFT, pady=10)
        global fil
        fil = None
        self.file_button = Button(file_controller, width=22, text="here", command=self.opensurf)
        self.file_button.pack(side=tk.RIGHT, pady=10)

        register_button = tk.Button(self, text="Register", height=3, width=30, command=self.whenreg)
        register_button.pack(pady=(10, 10))
        login_button = tk.Button(self, text="Log In", command=lambda: controller.show_frame(LogIn), height=3, width=30)
        login_button.pack(anchor='center', pady=10)
        quit_button = tk.Button(self, text="Quit",
                            command=lambda: controller.destroy_frame(), height=3, width=30)
        quit_button.pack(anchor='center', pady=10)

    def opensurf(self):
        """Opens the file selecting window and sends the file selected to the server"""
        global fil
        fil = tkFileDialog.askopenfile(parent=self, mode='r+b', title='Choose a file')  # opens file surfing

    def whenreg(self):
        """Handles the register protocol"""
        gotit = self.u_entry.get()
        if str(gotit).startswith("@"):
            gotit = gotit[1::]
        gotit2 = self.p_entry.get()
        hashgotit2 = hashlib.sha256(gotit2).hexdigest()
        client.client_socket.send('`' + str(gotit) + "#" + str(hashgotit2))
        if fil:
            file_string = fil.read(1024)
            while len(file_string) >= 1024:
                leng = str(len(file_string)).zfill(4)
                client.client_socket.send(leng)
                client.client_socket.send(file_string)
                file_string = fil.read(1024)
            client.client_socket.send(str(len(file_string)).zfill(4))
            client.client_socket.send(file_string)
            client.client_socket.send('0004')
            client.client_socket.send("done")
            client.client_socket.send(os.path.basename(fil.name))
            fil.close()
        else:
            client.client_socket.send('0004')
            client.client_socket.send('done')
        answer = client.client_socket.recv(1024)
        if not answer == "!":  # Get a response
            errorlabel = Label(self, text="Username or password is already taken :( ", fg="red")
            errorlabel.pack(anchor='center', pady=10)


def on_closing():
    """Kills the program"""
    client.get_socket().send("")
    raise SystemExit


client = Client()
app = App()
app.mainloop()



