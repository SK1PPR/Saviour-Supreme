import tkinter as tk
import os


    

CLIENT_PATH = "client_data"

absolute_path = os.path.dirname(__file__)

root = tk.Tk()

root.title("Saviour Supreme")
root.geometry("500x400")
root.resizable(0, 0)

'''Button functions'''

def info_button():
    print("Info button pressed")
    info_tab = tk.Toplevel(root,bg="#F1F0E8")
    info_tab.title("Welcome to Saviour Supreme")
    info_tab.geometry("400x300")
    root.resizable(0,0)
    T = tk.Text(info_tab,bg="#F1F0E8",fg="black")
    T.pack()
    quote = """HAMLET: To be, or not to be--that is the question:
    Whether 'tis nobler in the mind to suffer
    The slings and arrows of outrageous fortune
    Or to take arms against a sea of troubles
    And by opposing end them. To die, to sleep--
    No more--and by a sleep to say we end
    The heartache, and the thousand natural shocks
    That flesh is heir to. 'Tis a consummation
    Devoutly to be wished."""
    T.insert(tk.END, quote)

body = tk.Frame(root,bg="#F1F0E8")
body.pack(side=tk.TOP,fill="both",expand=1)

server_frame = tk.Frame(body,bg="#EEE0C9")
server_frame.pack(side=tk.LEFT,fill="both",expand=1,padx=10,pady=10)

server_header = tk.Frame(server_frame)
server_header.pack(side=tk.TOP,fill="x")

serverImg = tk.PhotoImage(file=os.path.join(absolute_path, "icons/cloud.png"))
tk.Button(server_header,image=serverImg).pack(side=tk.LEFT,padx=2,pady=2)

tk.Label(server_header,text="Server").pack(side=tk.LEFT,padx=2,pady=2)

server_footer = tk.Frame(server_frame)
server_footer.pack(side=tk.BOTTOM,fill="x")

deleteImg = tk.PhotoImage(file=os.path.join(absolute_path, "icons/trashbin.png"))
tk.Button(server_footer,image=deleteImg).pack(side=tk.RIGHT,padx=2,pady=2)

downloadImg = tk.PhotoImage(file=os.path.join(absolute_path, "icons/download.png"))
tk.Button(server_footer,image=downloadImg).pack(side=tk.RIGHT,padx=2,pady=2)

client_frame = tk.Frame(body,bg="#EEE0C9")
client_frame.pack(side=tk.RIGHT,fill="both",expand=1,padx=10,pady=10)

client_header = tk.Frame(client_frame)
client_header.pack(side=tk.TOP,fill="x")

clientImg = tk.PhotoImage(file=os.path.join(absolute_path, "icons/monitor.png"))
tk.Button(client_header,image=clientImg).pack(side=tk.LEFT,padx=2,pady=2)

tk.Label(client_header,text="Client").pack(side=tk.LEFT,padx=2,pady=2)

client_footer = tk.Frame(client_frame)
client_footer.pack(side=tk.BOTTOM,fill="x")

client_files_list = []
def client_files():
    files = os.listdir(CLIENT_PATH)      
    if len(files) == 0:
        tk.Label(client_frame,text="The server directory is empty",bg="#EEE0C9",fg="black")
    else:
        listbox = tk.Listbox(client_frame,bg="#EEE0C9",fg="black",border="0")
        index = 0
        for file in files:
            listbox.insert(index,file)
            client_files_list.append(file)
            index += 1
        listbox.pack(side="top",fill="both",expand=1,pady=5,padx=2)
            
client_files()

uploadImg = tk.PhotoImage(file=os.path.join(absolute_path, "icons/upload.png"))
tk.Button(client_footer,image=uploadImg).pack(side=tk.RIGHT,padx=2,pady=2)

infoImg = tk.PhotoImage(file=os.path.join(absolute_path, "icons/info.png"))
tk.Button(client_footer,image=infoImg,command=info_button).pack(side=tk.RIGHT,padx=2,pady=2)

footer = tk.Frame(root)
footer.pack(side=tk.BOTTOM,fill="x")

root.mainloop()