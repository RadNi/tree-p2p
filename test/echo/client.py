import threading
import time

from src.tools.simpletcp.clientsocket import ClientSocket

exitFlag = 0




# in_buf = ""


class Obj:
    def __init__(self):
        self.in_buf = ""

    def get_input(self):
        self.in_buf += input("command?")


s1 = ClientSocket("localhost", 5050, single_use=False)
response = s1.send("Hello, World!")

s2 = ClientSocket("localhost", 5050, single_use=False)
r1 = s2.send("Hello for the first time...")
r2 = s2.send("...and hello for the last!")
s2.close()
# s1.close()

# Display the correspondence
print("s1 sent\t\tHello, World!")
print("s1 received\t\t{}".format(response.decode("UTF-8")))
print("-------------------------------------------------")
print("s2 sent\t\tHello for the first time....")
print("s2 received\t\t{}".format(r1.decode("UTF-8")))
print("s2 sent\t\t...and hello for the last!.")
print("s2 received\t\t{}".format(r2.decode("UTF-8")))




c = threading.Condition()
flag = 0      #shared between Thread_A and Thread_B
val = 20
in_buf = ""

class Thread_A(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global flag
        global in_buf
        global val     #made global here
        while True:
            c.acquire()
            # if flag == 0:
            # print("A: val=" + str(val))
            in_buf = input("command?")
            time.sleep(0.1)
            flag = 1
            # val = 30
            c.notify_all()
            # else:
            c.wait()
            c.release()


class Thread_B(threading.Thread):
    def __init__(self, name, socket):
        threading.Thread.__init__(self)
        self.name = name
        self.socket = socket

    def run(self):
        global in_buf
        global flag
        global val    #made global here
        while True:
            c.acquire()
            # if flag == 1:
                # print("B: val=" + str(val))
            time.sleep(0.5)
            if in_buf != '':
                print(self.socket.send(in_buf))
            # flag = 0
            # val = 20
            c.notify_all()
        # else:
            c.wait()
            c.release()


a = Thread_A("myThread_name_A")
b = Thread_B("myThread_name_B", s1)

b.start()
a.start()

a.join()
b.join()