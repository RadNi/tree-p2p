# from  import Client
# from Listener import Listener
#
#
# # JSON read from 'file'
#
# def read_conf(file):
#     return None
#
#
# if __name__ == "__main__":
#     ls = Listener()
#
#     cl = Client(ls)
#
#     address = read_conf("addr.conf")
#
#     cl.connect(address[0].ip, address[0].port)
from src.Peer import Peer

if __name__ == "__main__":
    server = Peer("127.000.000.001", 5353, is_root=True)
    server.run()

    client = Peer("127.000.000.001", 3535, is_root=False, root_address=("127.000.000.001", 5353))

