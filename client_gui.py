#!/usr/bin/env python3
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
import os
import socket
from tqdm import tqdm
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 4476
ADDR = (IP,PORT)
FORMAT = 'utf-8'
SIZE = 1024
CLIENT_DATA_PATH = 'client_data'

PORT_DATA = 4556
ADDR_DATA = (IP, PORT)

admin = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

class GUI:
    def __init__(self):
        #Main GUI (hidden initially)
        self.window = Tk()
        self.window.withdraw()
        
        #Login window Layout
        self.login = Toplevel()
        self.login.title("Login")
        self.login.resizable(width=False,height=False)
        self.login.configure(width=400,height=300)
        self.pls = Label(self.login,text="Please login to continue",justify=CENTER,font="Helvetica 14 bold")
        self.pls.place(relheight=0.15,relx=0.2,rely=0.07)
        self.label_username = Label(self.login,text="Username: ",font="Helvetica 12")
        self.label_username.place(relheight=0.2,relx=0.1,rely=0.2)
        self.entry_username = Entry(self.login,font="Helvetica 14")
        self.entry_username.place(relwidth=0.4,relheight=0.12,relx=0.35,rely=0.2)
        self.entry_username.focus()
        self.label_password = Label(self.login,text="Password: ",font="Helvetica 12")
        self.label_password.place(relheight=0.2,relx=0.1,rely=0.35)
        self.entry_password = Entry(self.login,font="Helvetica 14",show="*")
        self.entry_password.place(relwidth=0.4,relheight=0.12,relx=0.35,rely=0.35)
        #Continue Button
        self.go = Button(self.login,text="CONTINUE",font="Helvetica 14 bold",command=lambda: self.go_ahead(self.entry_username.get(),self.entry_password.get()))
        self.go.place(relx=0.4,rely=0.55)
        self.window.mainloop()
        
    def go_ahead(self,name,password):
        self.name = name
        self.password = password
        #thread for receiving
        rcv = threading.Thread(target=self.receive)
        rcv.start()
        # #thread for sending
        # snd = threading.Thread(target=self.send)
        # snd.start()
     
    def begin_transfer(self,name):
        self.login.destroy()
        self.layout(name)
        
    def layout(self, name):
        self.window.deiconify()
        self.window.title(f"Logged in as {name}")
        self.window.geometry("500x400")
        self.window.minsize(500,400)
        self.window.maxsize(500,400)
        
        self.window.config(cursor='arrow')
        
        self.body = Frame(self.window,bg="#F1F0E8")
        self.body.pack(side=TOP,fill="both",expand=1)
        
        self.server_frame = Frame(self.body,bg="#EEE0C9")
        self.server_frame.pack(side=LEFT,fill="both",expand=1)
        self.server_header = Frame(self.server_frame)
        self.server_header.pack(side=TOP,fill="x")
        self.label_server = Label(self.server_header).pack(side=LEFT,padx=2,pady=2)
        
        self.serv_files = Text(self.server_frame, bg="#EEE0C9",fg="black",font="Helvetica 14",padx=5,pady=5)
        self.serv_files.place(relheight=1,relwidth=0.94)
        self.serv_files.config(state=DISABLED,highlightthickness=0)
        
        
        self.seperator = ttk.Separator(self.body,orient="vertical")
        self.seperator.place(relx=0.47, rely=0, relwidth=0.01, relheight=1)
        
        self.client_frame = Frame(self.body,bg="#EEE0C9")
        self.client_frame.pack(side=LEFT,fill="both",expand=1)
        self.client_header = Frame(self.client_frame)
        self.client_header.pack(side=TOP,fill="x")
        self.label_client = Label(self.client_header).pack(side=LEFT,padx=2,pady=2)
        
        '''Implementation of displaying the files'''
        
        self.footer = Frame(self.window)
        self.footer.pack(side=BOTTOM,fill="x")
        self.label_command = Label(self.footer,text="Command: ",font="Helvetica 12")
        self.label_command.pack(side=LEFT,padx=2,pady=2)
        self.entry_command = Entry(self.footer,font="Helvetica 14")
        self.entry_command.pack(side=LEFT,padx=2,pady=2)
        self.entry_command.focus()
        self.snd_button = Button(self.footer,text="Send", font = "Helvetica 12",command=lambda: self.send_button(self.entry_command.get()))
        self.snd_button.pack(side=RIGHT,padx=2,pady=2)
       
        
    def send_button(self,msg):
        self.msg = msg
        self.snd_button.config(state=DISABLED)
        self.entry_command.delete(0, END)
        
        def get_packet_count(filename):
            byte_size = os.stat(filename).st_size
            packet_count = byte_size // SIZE
            if byte_size % SIZE:
                packet_count += 1
            return packet_count

        self.msg = self.msg.split(' ')
        cmd = self.msg[0]
        
        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            client.close()
            self.login.destroy()
            self.window.destroy()
            self.snd_button.config(state=NORMAL)
            return
        elif cmd == "DELETE":
            client.send(f"{cmd}@{self.msg[1]}".encode(FORMAT))
        elif cmd == "UPLOAD":
            client_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_file.connect(ADDR_DATA)
            path = CLIENT_DATA_PATH + '/' + self.msg[1]
            if not os.path.exists(path):
                print(f"{self.msg[1]} does not exist")
                send_data = "INVALID"
                client.send(send_data.encode(FORMAT))
                self.snd_button.config(state=NORMAL)
                return
            filename = path.split("/")[-1]
            send_data = f"{cmd}@{filename}"
            client.send(send_data.encode(FORMAT))
            
            if not admin:
                self.snd_button.config(state=NORMAL)
                return
            
            packet_count = get_packet_count(path)
            bar = tqdm(range(packet_count), f"Sending {self.msg[1]}", unit="B", unit_scale=True, unit_divisor=1)
            f = open(path, "rb")
            print(f"Sending {path} with {packet_count} packets to server")
            while packet_count > 0 :
                client_file.send(f.read(SIZE))
                packet_count -= 1
                bar.update(1)
            f.close()
            client_file.close()   
        elif cmd == "DOWNLOAD":
            client_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_file.connect(ADDR_DATA)
            send_data = f"{cmd}@{self.msg[1]}".encode(FORMAT)
            client.send(send_data)
            
            received_file_name = CLIENT_DATA_PATH + '/' + self.msg[1].split("/")[-1]
            
            with open(received_file_name,"wb") as file:
                while True:
                    file_data = client_file.recv(SIZE)
                    if not file_data:
                        break
                    file.write(file_data)   
            client_file.close()      
        elif cmd == "CD":
            client.send(f"{cmd}@{self.msg[1]}".encode(FORMAT))
        elif cmd == "RENAME":
            client.send(f"{cmd}@{self.msg[1]}@{self.msg[2]}".encode(FORMAT))
        elif cmd == "MOVE":
            client.send(f"{cmd}@{self.msg[1]}@{self.msg[2]}".encode(FORMAT))
        else:
            send_data = "INVALID"
            client.send(send_data.encode(FORMAT))
        self.snd_button.config(state=NORMAL)
            
    def receive(self):
        while True:
            try:
                data = client.recv(SIZE).decode(FORMAT)
                data = data.split("@")
                cmd = data[0]
                msg = data[1]
                
                if cmd == "AUTH":
                    if msg == "Invalid credentials":
                        messagebox.showerror("INVALID CREDENTIALS", "Enterd invalid credentials, please try again")
                        client.close()
                        self.window.destroy()
                        break
                    
                    client.send(f"AUTH@{self.name}@{self.password}".encode(FORMAT))
                elif cmd == "DISCONNECTED":
                    client.close()
                    self.window.destroy()
                    break
                elif cmd == "OK":
                    self.begin_transfer(self.name)  
                elif cmd == "LIST":
                    print(msg)
                    self.serv_files.config(state=NORMAL)
                    self.serv_files.delete(1.0, END)
                    self.serv_files.insert(END, msg)
                    self.serv_files.config(state=DISABLED)
                    self.serv_files.see(END)
                elif cmd == "MSG":
                    messagebox.showinfo("SERVER RESPONSE", msg)       
                   
            except Exception as e:
                # an error will be printed on the command line or console if there's an error
                # print(f"An error occurred! :{e}")
                print(e)
                client.close()
                self.window.destroy()
                break
            
            
            
g = GUI()