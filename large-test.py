import os
from tqdm import tqdm

file_name = "large-file.txt"


data_list = []

if __name__ == '__main__':
    FILESIZE = os.stat(file_name).st_size
    bar = tqdm(range(FILESIZE), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
 
    with open(file_name, "rb") as file:
        while True:
            data = file.read(1)  # Read 1 KB at a time
            data_list.append(data)
            if not data:
                break
            bar.update(len(data))
            
            
    with open("dupl"+file_name, "wb") as file:
        for data in data_list:
            file.write(data)
