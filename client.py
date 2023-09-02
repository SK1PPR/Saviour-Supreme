import socket
import os
 
IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
CLIENT_DATA_PATH = "client_data"

PORT_DATA = 4556
ADDR_DATA = (IP, PORT_DATA)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    
    while True:
        data = client.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        msg = data[1]
 
        if cmd == "DISCONNECTED":
            print(f"[SERVER]: {msg}")
            break
        elif cmd == "OK":
            print(f"{msg}")
        elif cmd == "S":
            name, text = data[1], data[2]
            filepath = os.path.join(CLIENT_DATA_PATH, name)
            with open(filepath, "w") as f:
                f.write(text)

            print("File downloaded succesfully")
        elif cmd == "AUTH":
            print(f"{msg}")
            print("Are you a GUEST or ADMIN?\n")
            auth = input("> ")
            if auth == "GUEST":
                client.send("GUEST".encode(FORMAT))
            elif auth == "ADMIN":
                username = input("ENTER YOUR USERNAME: ")
                password = input("ENTER YOUR PASSWORD: ")
                data = f"ADMIN@{username}@{password}"
                client.send(data.encode(FORMAT))
            else:
                data = "INVALID"
                client.send(data.encode(FORMAT))
            continue
        
 
        data = input("> ")
        data = data.split(" ")
        cmd = data[0]
 
        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        elif cmd == "LIST":
            client.send(cmd.encode(FORMAT))
        elif cmd == "DELETE":
            client.send(f"{cmd}@{data[1]}".encode(FORMAT))
        elif cmd == "UPLOAD":
            path = data[1]

            with open(f"{path}", "r") as f:
                text = f.read()
 
            filename = path.split("/")[-1]
            send_data = f"{cmd}@{filename}@{text}"
            client.send(send_data.encode(FORMAT))
        elif cmd == "DOWNLOAD":
            client_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_file.connect(ADDR_DATA)
            send_data = f"{cmd}@{data[1]}".encode(FORMAT)
            client.send(send_data)
            
            received_file_name = CLIENT_DATA_PATH + '/' + data[1].split("/")[-1]
            
            with open(received_file_name,"wb") as file:
                while True:
                    file_data = client_file.recv(SIZE)
                    if not file_data:
                        break
                    file.write(file_data)   
            client_file.close()     
            
        else:
            send_data = "INVALID"
            client.send(send_data.encode(FORMAT))
            
    print("Disconnected from the server.")
    client.close()


if __name__ == '__main__':
    main()
