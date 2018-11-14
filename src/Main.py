from Client import Client
from Listener import Listener


# JSON read from 'file'

def read_conf(file):
    return None


if __name__ == "__main__":
    ls = Listener()

    cl = Client(ls)

    address = read_conf("addr.conf")

    cl.connect(address[0].ip, address[0].port)
