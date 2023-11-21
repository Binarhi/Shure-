from M32APi import *
import threading
from ShureAP import *
from pythonosc.udp_client import SimpleUDPClient
import time
#from interface import *
import concurrent.futures
import json


#For testing purposes!!---------------------------------------------------------------------------------------------------------------
#X32_IP='192.168.0.100'
#mics = [{'receiver_ip': '192.169.0.78', 'receiver_x32_ch': '01', 'receiver_type':'SLXD' , 'receiver_name':'Clarol', 'receiver_ch': 1}, 
       # {'receiver_ip': '192.169.0.76', 'receiver_x32_ch': '02', 'receiver_type':'SLXD' , 'receiver_name':'Phl', 'receiver_ch': 1}]
#_____________________________________________________________________________________________________________________________________
Threads =[]

update_entries_table()
root.mainloop()

print('boyyyy')
s = socket(AF_INET,SOCK_DGRAM)
msg =  "/xremote"


def load_data():
    global mics, toggle_state, X32_IP
    try:
        with open("Mics.txt", "r") as file:
            loaded_data = json.load(file)
            mics = loaded_data.get("mics", [])
            X32_IP = str(loaded_data.get('X32_IP'))
            entry_m32_ip.delete(0, tk.END)
            entry_m32_ip.insert(0, loaded_data.get("X32_IP", "192.168.0.100"))
            toggle_state = loaded_data.get("toggle_state", False)
    except FileNotFoundError:
        print("")
      
        # Handle the case when the file is not found
for mic in mics:
    X32_IP = mic['M32 IP']
print(f"X32_IP: {X32_IP}")
print(mics)
con = Console(X32_IP)
client_CONSOLE = SimpleUDPClient(X32_IP, 10023)  # Create client
startr = threading.Thread(target=con.trig)
startr.start()
def Console_updater ():
     for mic in mics:
   
     
        updater = "/ch/"+str(mic['receiver_x32_ch'])+"/config/name" 
        val = mic['receiver_name']
        print(updater, [val])

        client_CONSOLE.send_message(updater, [val])
          
def Receiver_updater ():
     for mic in mics:
        #create the  Shure Receiver Clients
        client_Receiver = SimpleUDPClient(mic['receiver_ip'], 2022) 
     
        updater =f"< SET {mic['receiver_ch']} CHAN_NAME >" 
        val = f"{mic['receiver_name']}"
        print(updater, [val])

        client_Receiver.send_message(updater, [val])

def Polls():
    for mic in mics:
        Solo_Parser= Receiver(con, mic['receiver_type'], mic['receiver_x32_ch'], mic['receiver_ip'], mic['receiver_ch'], mic['receiver_name']) 
        Solo_Btn=threading.Thread(target=Solo_Parser.Is_Soloed)
        Threads.append(Solo_Btn)  
    try:
      for _ in Threads:
        _()
    except:
      pass


try:
    Console_updater()
    Receiver_updater()
except error as er:
    print(f'cannot establish connection because of the fatal error, {er}') 

def toggle_script():
    try:
        print('hello')
        #poll=threading.Thread(target=Solo_Parser.Is_Soloed)
        #poll.start()
        print("Script is running.")
        sub = threading.Thread(target=con.subscribe)
        sub.start()
       
        for mic in mics:
            rec = Receiver(con, mic['receiver_type'], mic['receiver_x32_ch'], mic['receiver_ip'], mic['receiver_ch'],
                            mic['receiver_name'])
            poll = threading.Thread(target=rec.poller)
            poll.start()

    except error as err:
        print(f'Error occured because{err}')


Alpha=threading.Thread(target=toggle_script)
Alpha.start()
Beta=threading.Thread(target=Polls)
Beta.start()

#_____________________________________________________________________________________
'''if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Submit CPU-bound tasks to the process pool
        futures = [executor.submit(start_interface), executor.submit(toggle_script)]

        # Wait for the tasks to complete
        concurrent.futures.wait(futures)
'''


