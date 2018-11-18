from src.tools.simpletcp.tcpserver import TCPServer

from src.tools.simpletcp.clientsocket import ClientSocket


class Stream:

    def __init__(self, ip, port):
        self.messages_dic = {}
        self.server_in_buf = {}
        self.parent = (None, None)  #TODO   fill this later as (ip, port)

        def cb(ip, queue, data):
            queue.put(bytes('ACK'))
            # self.messages_dic.update({ip: self.messages_dic.get(ip).append(data)})
            self.server_in_buf.update({ip, data})

        self.server = TCPServer(ip, port, cb)
        self.clients = []

    def add_client(self, ip, port):
        self.messages_dic[(ip, port)] = []
        self.clients.append(ClientSocket(ip, port))

    def remove_client(self, cl):
        self.clients.remove(cl)
        cl.close()
        self.messages_dic.pop((cl.connect_ip, cl.connect_port))

    def read_in_buf(self):
        return self.server_in_buf

    def send_message(self, client, message):
        self.messages_dic.update({client, self.messages_dic.pop(client).append(message)})
