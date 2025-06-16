import socket 
import time

class XCS (object):
    def __init__(self, hostname):
        self.hostname = hostname
        self.fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fd.settimeout(60.0)
        self.port = 4944
        self.fd.connect((self.hostname, self.port))
        
    def __del_(self):
        self.fd.close()
        
    def receive(self): 
        buf = ""
        while True:
            data = self.fd.recv(16384).decode('iso-8859-1')
            buf += data
            len_data=len (data)
            if len_data < 1:
                break
            if data[len_data-1] == "\n":
                break
        return buf
    
    def send(self, data):
        send_msg = data + "\n"
        self.fd.sendall (send_msg.encode())
    
def wait_for_state_transition (xcs, timeout=300.0):
    time.sleep(1.0)
    print("waiting for state transition...")
    start = time.time()
    while True:
        xcs.send("state?")
        rec = xcs.receive()
        print("state = " + rec)
        if not rec.endswith("...'\n"):
            print("state transition finished")
            return
        assert time.time() - start < timeout, "state transition timeout"
        time.sleep(2.0)
        