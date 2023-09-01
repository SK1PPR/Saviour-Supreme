import os
import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = 'utf-8'
SERVER_DATA_PATH = "server_data"

user_credentials = {
    'user1': 'password1',
    'user2': 'password2',
}

#create different commands for different users and allow access to different commands accordingly
#admin-users can upload/download files from the server
#guest-users can only download files from the server
#super-admin-users can upload/download files from the server and have access to hidden files, he can also add usernames and passwords
#All user commands

def list(conn):
    files = os.listdir(SERVER_DATA_PATH)
    send_data = "OK@"
       
    if len(files) == 0:
        send_data += "The server directory is empty"
    else:
        send_data += "\n".join(f for f in files)
    conn.send(send_data.encode(FORMAT))

def upload(conn,data):
    name, text = data[1], data[2]
    filepath = os.path.join(SERVER_DATA_PATH, name)
    with open(filepath, "w") as f:
        f.write(text)
        
    send_data = "OK@File uploaded successfully."
    conn.send(send_data.encode(FORMAT))

def delete(conn,data):
    files = os.listdir(SERVER_DATA_PATH)
    send_data = "OK@"
    filename = data[1]
 
    if len(files) == 0:
        send_data += "The server directory is empty"
    else:
        if filename in files:
            os.system(f"rm {SERVER_DATA_PATH}/{filename}")
            send_data += "File deleted successfully."
        else:
            send_data += "File not found."
 
    conn.send(send_data.encode(FORMAT))
    
def invalid(conn):
    send_data = "OK@Invalid Command"
    conn.send(send_data.encode(FORMAT))

def logout(conn,addr):
    print(f'[DISCONNECTED] {addr} disconnected')
    conn.close()
    
def help_guest(conn):
    data = "OK@"
    data += "LIST: List all the files from the server.\n"
    data += "DOWNLOAD <filename>: Download a file from the server.\n"
    data += "LOGOUT: Disconnect from the server.\n"
    data += "HELP: List all the commands."
 
    conn.send(data.encode(FORMAT))

def help_admin(conn):
    data = "OK@"
    data += "LIST: List all the files from the server.\n"
    data += "UPLOAD : Upload a file to the server.\n"
    data += "DELETE : Delete a file from the server.\n"
    data += "DOWNLOAD <filename>: Download a file from the server.\n"
    data += "LOGOUT: Disconnect from the server.\n"
    data += "HELP: List all the commands."
 
    conn.send(data.encode(FORMAT))

def access_denied(conn):
    conn.send("OK@Access Denied")
    
def download(conn,data):
    path = SERVER_DATA_PATH + data[1]
    
    with open(f"{path}", "r") as f:
        text = f.read()
 
    filename = path.split("/")[-1]
    send_data = f"NOR@{filename}@{text}"
    conn.send(send_data.encode(FORMAT))



#main function
def main():
    ''' Creating a TCP server socket'''
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print('[LISTENING] Server is listening...')
    
    ''' Accepting connections from clitens'''
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn,addr)).start()
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')
        
        
def handle_client(conn,addr):
    print(f'[NEW CONNECTION] {addr} connected')
    conn.send("AUTH@Welcome to the file server!".encode(FORMAT))
    
    data = conn.recv(SIZE).decode(FORMAT)
    data = data.split("@")
    cmd = data[0]
    
    
    if cmd == "GUEST":
        handle_guest(conn,addr)       
    elif cmd == "INVALID":
        conn.send("AUTH@Invalid Command".encode(FORMAT))
    else:
        if data[1] in user_credentials and user_credentials[data[1]] == data[2]:
            handle_admin(conn,addr)
        else:
            conn.send("AUTH@Invalid Credentials".encode(FORMAT)) 
        
def handle_guest(conn,addr):
    conn.send("OK@Entered file server as guest".encode(FORMAT))
    # help_guest(conn)
    
    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        
        if cmd == "LIST":
            list(conn)
        elif cmd == "UPLOAD":
            access_denied(conn)
        elif cmd == "DELETE":
            access_denied(conn) 
        elif cmd == "INVALID":
            invalid(conn)
        elif cmd == "LOGOUT":
            logout(conn,addr)
            break
        elif cmd == "HELP":
            help_guest(conn)
        elif cmd == "DOWNLOAD":
            download(conn,data)
        
def handle_admin(conn,addr):
    conn.send("OK@Entered file server as admin".encode(FORMAT))
    # help_admin(conn)
    
    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        
        if cmd == "LIST":
            list(conn)
        elif cmd == "UPLOAD":
            upload(conn,data)
        elif cmd == "DELETE":
            delete(conn,data) 
        elif cmd == "INVALID":
            invalid(conn)
        elif cmd == "LOGOUT":
            logout(conn,addr)
            break
        elif cmd == "HELP":
            help_admin(conn)
    
    
if __name__ == '__main__':
    main()
    