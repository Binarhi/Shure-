from oscpy.server import OSCThreadServer
from socket import *
from time import sleep

s = socket(AF_INET,SOCK_DGRAM)
sock = socket(AF_INET, SOCK_DGRAM)
msg =  "/xremote"
def two_digits(ch):
    if ch < 10:
        ch = "0" + str(ch)
    else:
        ch = str(ch)
    return ch

class Console:
    def __init__(self, console_ip):
        self.console_ip = console_ip
        self.console_port = 10023
        self.name_list = []

        # Initialize name_list with 32 empty strings.
        for n in range(32):
            self.name_list.append("")

        # Setup socket to console connection and start listening
        hostname = gethostname()
        local_ip = gethostbyname(hostname)
        self.server = OSCThreadServer(advanced_matching=True)
        self.sock = self.server.listen(address=local_ip, port=0, default=True)
        self.server.bind(b"/ch/../config/name", self.callback, sock=self.sock, get_address=True)
        print("Listening to console at", self.console_ip)

        # Query for all channel names
        for ch in range(1, 33):
            ch = two_digits(ch)
            message = "/ch/" + ch + "/config/name"
            self.message(message, "")

    def Is_Soloed(self):
          while True:
               datarr = s.recv(1024)
               z = str(datarr)
               x_b = z.replace('\\x00\\x00\\x00\\x00','')
               
               
               files = x_b.split(',')
               #print (data)
               #print(files[0]) #, end= '\r')
               #print(files[1])
               
               #if files[0]=="b'/-stat/solosw/"+str(receiver_ch) and files[1] == "i\x00\x01'":
               if ("b'/-stat/solosw/"+str(self.receiver_x32_ch))==files[0] and  (r"i\x00\x01'") ==files[1]:
                    print(f'FLasH for me {self.receiver_name}')
                    try:
                         sock.connect((self.receiver_ip, 2022))
                         sock.send(bytes(f'< SET {self.receiver_x32_ch} FLASH ON >', encoding='ascii'))
                    except error as e:
                         print(f'Receiver, {self.receiver_name} @ IP: {self.receiver_ip} is not online! because of the error, {e}')

               #if files[0]=="b'/-stat/solosw/"+str(receiver_ch) and files[1] == "i \x00\x00'":
               if ("b'/-stat/solosw/"+str(self.receiver_x32_ch))==files[0] and  (r"i\x00\x00'") ==files[1]:
                    print(f'UnFlash for me {self.receiver_name}')
                    try:
                         sock.connect((self.receiver_ip, 2022))
                         sock.send(bytes(f'< SET {self.receiver_x32_ch} FLASH OFF >', encoding='ascii'))
                    except error as e :
                         print(f'Receiver, {self.receiver_name} @ IP: {self.receiver_ip} is not online!, because of the error, {e} ')
    
    def trig(self):
    # while True:
        try:
            s.sendto(bytes(msg, 'utf-8'),(self.console_ip,10023))
            sleep(7)
            #print(f'Subscribing to the Console @ :{X32_IP}')
            
        except error as e:
            pass

    def callback(self, address, values):
        # Extract channel number from address string
        address = str(address)
        channel = int(address[6:8])

        # Extract channel name string
        values = str(values)
        name = values[2: -1]

        # Find if there are battery bars in the name and remove.
        batt_indicator = name.find(" (")
        if batt_indicator > -1:
            name = name[:batt_indicator]
            value = bytes(name, 'utf-8')
            name_message = "/ch/" + two_digits(channel) + "/config/name"
            self.message(name_message, value)

        # Find if there are h:mm in the name and remove.
        batt_indicator = name.find(":")
        if batt_indicator > -1:
            name = name[:batt_indicator - 2]
            value = bytes(name, 'utf-8')
            name_message = "/ch/" + two_digits(channel) + "/config/name"
            self.message(name_message, value)

        # Add channel name into the name list at the appropriate index
        self.name_list[channel - 1] = name
        self.duplicate_names(channel)

    def subscribe(self):
        # Subscribe to console updates via OSC /xremote command.
        while True:
            self.server.send_message(b"/xremote", "", self.console_ip, self.console_port, sock=self.sock, safer=True)
            sleep(5)


   

    def message(self, message, value):
        try:
        # Send one OSC message to console.
         self.server.send_message(bytes(message, 'utf-8'), value, self.console_ip, self.console_port, sock=self.sock, safer=True)
        except error as e:
            pass

    def duplicate_names(self, ch):
        dups = []
        a = self.name_list[ch - 1]

        # Search through all values in self.name_list and compare with ch.
        # Do not compare to itself, ignore blank channels.
        for y in range(32):
            b = self.name_list[y]
            if (ch - 1) != y:
                if a == b and a != "":
                    dups.append(ch)
                    dups.append(y + 1)

        # Report duplicate channels from temporary duplicate list, sort, and print warning message.
        dups = list(set(dups))
        dups.sort()
        if len(dups) > 1:
            print('Warning: Duplicate channel name!  Channels ' + str(dups)[1:-1] + ' = ' + self.name_list[ch - 1])
            