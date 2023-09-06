#!/usr/bin/env python3
import PySimpleGUI as sg
import os
import socket
import threading
from tqdm import tqdm
import shutil
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
my_eip = s.getsockname()[0]
s.close()

SERVER_PATH = ""
SERVER_PASS = ""
CLIENT_DOWN = ""
msg = ""

PORT = 4456
PORT_DATA = 4556
FORMAT = 'utf-8'
SIZE = 1024
ADDR = (my_eip,PORT)
ADDR_DATA = (my_eip,PORT_DATA)

STOP_THREADS = False

CLIENTS = []

THREADS = []

THEME = 'DarkGray4'

class Client:
    global my_eip
    global PORT
    def __init__(self,is_admin):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((my_eip,PORT))
        if(is_admin):
            layout = [[sg.Text('Enter password: '),sg.InputText(key='password',font=16,password_char='*')],
                      [sg.Button('Submit')]]
            window = sg.Window('Authentication', layout, element_justification='c')
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED:
                    break
                elif event == 'Submit':
                    msg = values['password']
                    self.sock.send(f'T2@@{msg}'.encode(FORMAT))
                    break
            window.close()
        else:
            self.sock.send('T1'.encode(FORMAT))
        

        self.create_window()
        
    
    #change directory, move
    def create_window(self):
        first_col = [[sg.Listbox(values=[],size=(40, 20), key="file_list")]]
        second_col = [[sg.Button('Help')],
                      [sg.Button('Download')],
                      [sg.Button('Delete')],
                      [sg.Button('Upload')],
                      [sg.Button('Rename')],
                      [sg.Button('Logout')],
                      [sg.Button('CD'),sg.Button('./')]]
        layout = [[sg.Column(first_col), sg.VSeparator(), sg.Column(second_col)],
                  [sg.HSeparator()],
                  [sg.Text('Server Response: '), sg.Input(size=(20,1),font=16,key='resp',disabled=True)]]
        self.window = sg.Window(f'Joined {my_eip}', layout, element_justification='c')
        
        t = threading.Thread(target=self.receive)
        THREADS.append(t)
        t.start()
        
        while True:
            global STOP_THREADS
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == 'Logout':
                self.sock.send('LOGOUT'.encode(FORMAT))
                self.sock.close()
                self.window.close()
                STOP_THREADS = True
                for t in THREADS:
                    t.join()
                break
            elif event == 'Help':
                self.sock.send('HELP'.encode(FORMAT))
            elif event == 'Delete':
                file = values['file_list'][0]
                msg = f'DELETE@@{file}'.encode(FORMAT)
                self.sock.send(msg)
            elif event == 'Download':
                file = values['file_list'][0]
                self.sock.send(f'DOWNLOAD@@{file}'.encode(FORMAT))
            elif event == 'Upload':
                file = sg.popup_get_file('Select a file',title='Upload File')
                print(file)
                if not file == 'None':
                    self.sock.send(f'UPLOAD@@{file}'.encode(FORMAT))
            elif event == 'Rename':
                text = sg.popup_get_text('Enter new filename',title='Rename')
                filen = values['file_list'][0]
                msg = f'RENAME@@{filen}@@{text}'
                self.sock.send(msg.encode(FORMAT))
            elif event == 'CD':
                folder = values['file_list'][0].split('.')
                if len(folder)==1:
                    msg = f'CD@@{folder[0]}'
                    self.sock.send(msg.encode(FORMAT))
                else:
                    #add download file and open feature here
                    self.change_val('Invalid Diectory')
            elif event == './':
                self.sock.send('CD@@./'.encode(FORMAT))
                    
                    
                    
    
    def change_val(self,message):
        self.window['resp'].update(disabled=False)
        self.window['resp'].update(message)
        self.window['resp'].update(disabled=True)
        
    def change_list(self,val):
        self.window['file_list'].update(val)
               
    def receive(self):
        time.sleep(0.1)
        while True:
            global CLIENT_DOWN
            try:
                data = self.sock.recv(SIZE).decode(FORMAT)
                data = data.split('@@')
                cmd = data[0]
                if cmd == 'ERR':
                    self.sock.close()
                    self.window.close()
                    break
                elif cmd == 'OK':
                   self.change_val('Server granted access!')
                elif cmd == 'HELP':
                    sg.popup_no_buttons(data[1],non_blocking=True)
                elif cmd == 'MSG':
                    self.change_val(data[1])
                elif cmd == 'LIST':
                    val = data[1].split('\n')
                    self.change_list(val)
                elif cmd == 'DOWN':
                    self.sock_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock_data.connect((my_eip,PORT_DATA))
                    file_name = CLIENT_DOWN + '/' + data[1].split('/')[-1]
                        
                    with open(file_name, 'wb') as file:
                        while True:
                            file_data = self.sock_data.recv(SIZE)
                            if not file_data:
                                break
                            file.write(file_data)
                    self.sock_data.close()
                    self.change_val(f'Downloaded {file_name} successfully')
                elif cmd == 'UPL':
                    self.sock_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock_data.connect((my_eip, PORT_DATA))
                    
                    path = data[1]
                    
                    byte_size = os.stat(path).st_size
                    packet_count = byte_size // SIZE
                    if byte_size % SIZE:
                        packet_count += 1
                        
                    f = open(path, 'rb')
                    self.change_val(f'Sending {packet_count} packets')
                    while packet_count > 0:
                        self.sock_data.send(f.read(SIZE))
                        packet_count -= 1
                    f.close()
                    self.sock_data.close()
                    
                    
                if STOP_THREADS :
                    break
            except:
                continue
          
class Server:
    global my_eip
    global CLIENTS
    global SERVER_PASS
    global SERVER_PATH
    global STOP_THREADS
    def __init__(self):
        global CLIENTS
        global STOP_THREADS
        layout = [[sg.Text(f'Server is listening on {my_eip}')],
                [sg.Multiline(size=(60,20),font=16,key='textbox',disabled=True)],
                [sg.Button('Close'),sg.Button('Change')]]
        self.window = sg.Window('Server Logs', layout, element_justification='c')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(ADDR)
        self.sock.listen()
        self.server_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_data.bind(ADDR_DATA)
        self.server_data.listen()
        
        t = threading.Thread(target=self.server_handler)
        THREADS.append(t)
        t.start()
            
        while True:
            event, self.values = self.window.read()
            if event == sg.WIN_CLOSED or event == 'Close':
                self.window.close()
                self.sock.close()
                STOP_THREADS = True
                for t in THREADS:
                    t.join()
                break
            elif event == 'Change':
                for client in CLIENTS:
                    client.send('OK'.encode(FORMAT))
                self.change_val('Password changed!')
                
        
    
    def server_handler(self):
        while True:
            try: 
                conn, addr = self.sock.accept()
                CLIENTS.append(conn)
                show = f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}\n'
                self.change_val(show)
                t = threading.Thread(target=self.handle_client, args=(conn, addr))
                THREADS.append(t)
                t.start()
                if STOP_THREADS :
                    break
            except:
                continue
            
    
    def change_val(self,message):
        global msg
        self.window['textbox'].update(disabled=False)
        msg += message
        self.window['textbox'].update(msg)
        self.window['textbox'].update(disabled=True)
        
    def handle_client(self,conn, addr):
        msg = f'[NEW CONNECTION] {addr} connected\n'
        self.change_val(msg)
        
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split('@@')
        cmd = data[0]
        time.sleep(3)
        if cmd == 'T1':
            self.handle_guest(conn,addr)
        elif cmd == 'T2' and data[1] == SERVER_PASS:
            self.handle_admin(conn,addr)
        else:
            msg = 'ERR'
            conn.send(msg.encode(FORMAT))
            conn.close()
        
    
    def handle_guest(self,conn,addr):
        conn.send("OK".encode(FORMAT))
        time.sleep(0.1)
        global SERVER_PATH
        local_server_path = SERVER_PATH
        self.send_dir(conn,local_server_path)
        

    
        while True:
            data = conn.recv(SIZE).decode(FORMAT)
            data = data.split("@@")
            cmd = data[0]
        
            if cmd == "LIST":
                self.send_dir(conn,local_server_path)
            elif cmd == "UPLOAD":
                self.access_denied(conn)
            elif cmd == "DELETE":
                self.access_denied(conn) 
            elif cmd == "INVALID":
                self.invalid(conn)
            elif cmd == "LOGOUT":
                self.logout(conn,addr)
                break
            elif cmd == "HELP":
                self.help_guest(conn)
            elif cmd == "DOWNLOAD":
                self.download(conn,data,local_server_path)
            elif cmd == "CD":
                local_server_path = self.change_dir(conn,data,local_server_path)
            elif cmd == "RENAME":
                self.invalid(conn)
            elif cmd == "MOVE":
                self.invalid(conn)
            
            if STOP_THREADS:
                break
    
    
    def handle_admin(self,conn,addr):
        conn.send('OK'.encode(FORMAT))
        time.sleep(0.1)
        global SERVER_PATH
        local_server_path = SERVER_PATH
        self.send_dir(conn,local_server_path)
        
        while True:
            data = conn.recv(SIZE).decode(FORMAT)
            data = data.split('@@')
            cmd = data[0]
            
            if cmd == "LIST":
                self.send_dir(conn,local_server_path)
            elif cmd == "UPLOAD":
                self.upload(conn,data,local_server_path)
            elif cmd == "DELETE":
                self.delete(conn,data,local_server_path) 
            elif cmd == "INVALID":
                self.invalid(conn)
            elif cmd == "LOGOUT":
                self.logout(conn,addr)
                break
            elif cmd == "HELP":
                self.help_admin(conn)
            elif cmd == "DOWNLOAD":
                self.download(conn,data,local_server_path)
            elif cmd == "CD":
                local_server_path = self.change_dir(conn,data,local_server_path)
            elif cmd == "RENAME":
                self.rename(conn,data,local_server_path)
            elif cmd == "MOVE":
                self.move(conn,data)
                
            if STOP_THREADS:
                break
                
                
    #commands
    def send_dir(self,conn,local_server_dir):
        files = os.listdir(local_server_dir)
        send_data = "LIST@@"
       
        if len(files) == 0:
            send_data += "The server directory is empty"
        else:
            send_data += "\n".join(f for f in files)
        conn.send(send_data.encode(FORMAT))

    def upload(self,conn,data,path):
        msg = f'UPL@@{data[1]}'
        conn.send(msg.encode(FORMAT))
        conn_data, addr_data = self.server_data.accept()
        
    
        received_file_name = path + '/' + data[1].split("/")[-1]
        self.change_val(f"{addr_data} uploading {received_file_name}\n")
        with open(received_file_name,"wb") as file:
            while True:
                file_data = conn_data.recv(SIZE)
                if not file_data:
                    break
                file.write(file_data)   

        conn.send('MSG@@File uploaded successfully'.encode(FORMAT))
        time.sleep(0.1)
        self.send_dir(conn,path)

    def delete(self,conn,data,path):
        files = os.listdir(path)
        send_data = "MSG@@"
        filename = data[1]
 
        if len(files) == 0:
            send_data += "The server directory is empty"
        else:
            if filename in files:
                os.system(f"rm {path}/{filename}")
                send_data += "File deleted successfully."
            else:
                send_data += "File not found."
 
        conn.send(send_data.encode(FORMAT))
        time.sleep(0.1)
        self.send_dir(conn,path)
    
    def invalid(self,conn):
        send_data = "MSG@@Invalid Command"
        conn.send(send_data.encode(FORMAT))

    def logout(self,conn,addr):
        self.change_val(f'[DISCONNECTED] {addr} disconnected')
        conn.close()
    
    def help_guest(self,conn):
        data = "HELP@@"
        data += "WELCOME TO THE SERVER AS GUEST\n"
        data += "LIST: List all the files from the server.\n"
        data += "CD <dir_name>: Change directory on the server\n"
        data += "CD ./ : Go to parent directory on the server\n"
        data += "DOWNLOAD <filename>: Download a file from the server.\n"
        data += "LOGOUT: Disconnect from the server.\n"
        data += "HELP: List all the commands."
 
        conn.send(data.encode(FORMAT))

    def help_admin(self,conn):
        data = "HELP@@"
        data+= "WELCOME TO THE SERVER ADMINISTRATOR\n"
        data += "LIST: List all the files from the server.\n"
        data += "UPLOAD <filename>: Upload a file to the server.\n"
        data += "CD <dir_name>: Change directory on the server\n"
        data += "CD ./ : Go to parent directory on the server\n"
        data += "RENAME <original_filename> <new_filename>: Rename a file on the server\n"
        data += "DELETE : Delete a file from the server.\n"
        data += "DOWNLOAD <filename>: Download a file from the server.\n"
        data += "MOVE <curr_dir> <final_dir>: Move a file in the server\n"
        data += "LOGOUT: Disconnect from the server.\n"
        data += "HELP: List all the commands."
 
        conn.send(data.encode(FORMAT))

    def access_denied(self,conn):
        conn.send("MSG@@Access Denied".encode(FORMAT))
    
    
    def get_packet_count(self,filename):
        byte_size = os.stat(filename).st_size
        packet_count = byte_size // SIZE
        if byte_size % SIZE:
            packet_count += 1
        return packet_count   
    

    def download(self,conn,data,local_server_path):
        path =  local_server_path+ "/" + data[1]
    
        if not os.path.exists(path):
            send_data = "MSG@@FILE NOT FOUND"
            conn.send(send_data.encode(FORMAT))
            return

        else:
            conn.send(f'DOWN@@{path}'.encode(FORMAT))
            conn_data, addr_data = self.server_data.accept()    
        
        packet_count = self.get_packet_count(path)
    
        bar = tqdm(range(packet_count), f"Sending {data[1]}", unit="B", unit_scale=True, unit_divisor=1024)
        f = open(path, "rb")
        self.change_val(f"Sending {path} with {packet_count} packets to {addr_data}\n")
        while packet_count > 0 :
            conn_data.send(f.read(SIZE))
            packet_count -= 1
            bar.update(1024)
        f.close()
        conn.send("MSG@@DOWNLOADED FILE".encode(FORMAT))

    def change_dir(self,conn, data,local_server_path):
        global SERVER_PATH
        if data[1] == "./":
            if local_server_path == SERVER_PATH:
                send_data = "MSG@@ALREADY AT ROOT"
                conn.send(send_data.encode(FORMAT))
            else:
                temp = local_server_path.split('/')
                temp.pop()
                ret_path = '/'.join(temp)
                self.send_dir(conn,ret_path)
                return ret_path
            
        elif not os.path.exists(local_server_path+'/'+data[1]):
            send_data = "MSG@@INVALID DIRECTORY"
            conn.send(send_data.encode(FORMAT))
    
        else:
            ret_path = local_server_path +'/'+ data[1] 
            send_data = f"MSG@@Directory changed to {data[1]}"
            conn.send(send_data.encode(FORMAT))
            time.sleep(0.1)
            self.send_dir(conn,ret_path)
            return ret_path
 
        return local_server_path

    def rename(self,conn,data,path):
        path_init = path+'/' + data[1]
        path_final = path+ '/' + data[2]
        try:
            os.rename(path_init, path_final)
            send_data = "MSG@RENAME SUCCESSFUL"
            conn.send(send_data.encode(FORMAT))
            self.change_val(f'{conn} changed {path_init} to {path_final}')
            time.sleep(0.1)
            self.send_dir(conn, path)
        except FileNotFoundError:
            send_data = "MSG@FILE NOT FOUND"
            conn.send(send_data.encode(FORMAT))
        except OSError as e:
            print(f"An error occurred while renaming the file: {e}")
            send_data = "MSG@INVALID COMMAND"
            conn.send(send_data.encode(FORMAT))
        
    
    def move(self,conn,data):
        path_init = os.path.join(SERVER_PATH,data[1])
        path_final = os.path.join(SERVER_PATH,data[2])
        try:
            shutil.move(path_init, path_final)
            send_data = "MSG@FILE MOVED SUCCESSFULLY"
            conn.send(send_data.encode(FORMAT))  
        except FileNotFoundError:
            send_data = "MSG@FILE NOT FOUND"
            conn.send(send_data.encode(FORMAT))
        except OSError as e:
            self.change_val(f"An error occurred while moving the file: {e}")
            send_data = "MSG@@INVALID COMMAND"
            conn.send(send_data.encode(FORMAT))
        # else:
        #     for client in clients:
        #         list(client)
        
def start_server():
    global SERVER_PASS
    sg.theme(THEME)
    layout = [[sg.Text('The last step ...')],
              [sg.Text('Password for admin login: ',font=16), sg.InputText(key='password',font=16)],
              [sg.Button('Create')]]
    window = sg.Window('Credentials',layout,element_justification='c')
    while True:
        event,values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == 'Create':
            SERVER_PASS = values['password']
            window.close()
            Server()
            break
    
def create():
    global SERVER_PATH
    sg.theme(THEME)
    layout = [[sg.Text('Create your server', size=(15,1), font=40, justification='c')],
              [sg.Text('Choose Server location: '), sg.FolderBrowse(key='IN')],
              [sg.Button('Submit'), sg.Button('Exit')]]
    window = sg.Window('Server Settings',layout, element_justification='c')
    while True:
        event,values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            break
        elif event == 'Submit':
            SERVER_PATH = values['IN']
            window.close()
            start_server()
            break

def join():
    global CLIENT_DOWN
    global my_eip
    sg.theme(THEME)
    layout = [[sg.Text('Join a server', size=(15,1), font=40, justification='c')],
              [sg.Text('Enter the server IP Address: '), sg.InputText(key='IP',font=16)],
              [sg.Text('Select download folder:') , sg.FolderBrowse(key='download')],
              [sg.Button('Guest'), sg.Button('Admin'), sg.Button('Exit')]]
    window = sg.Window('Join Server', layout, element_justification='c')
    while True:
        events, values = window.read()
        if events == sg.WIN_CLOSED or events == 'Exit':
            break
        elif events == 'Guest' or events == 'Admin':
            my_eip = values['IP']
            CLIENT_DOWN = values['download']
            if events == 'Admin':
                window.close()
                Client(True)
            else :
                window.close()
                Client(False)
            break
    

def welcome():
    sg.theme(THEME)
    layout = [[sg.Text("Welcome to Saviour Supreme",size=(25,1),font=40,justification='c')],
              [sg.Button('Create'),sg.Button('Join'),sg.Button('Cancel')]]
    window = sg.Window('Welcome',layout,element_justification='c')
    
    while True:
        event = window.read()[0]
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        elif event == 'Create':
            window.close()
            create()
            break
        elif event == 'Join':
            window.close()
            join()
            break
        
welcome()
