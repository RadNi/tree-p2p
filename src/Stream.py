from simpletcp.tcpserver import TCPServer

from src.tools.simpletcp.clientsocket import ClientSocket


class Stream:

    def __init__(self, ip, port):
        self.messages_dic = {}

        def cb(ip, queue, data):
            queue.put(bytes('ACK'))
            self.messages_dic.update({ip: self.messages_dic.get(ip).append(data)})

        self.server = TCPServer(ip, port, cb)
        self.clients = []

    def add_client(self, ip, port):
        self.messages_dic[(ip, port)] = []
        self.clients.append(ClientSocket(ip, port))

    def remove_client(self, cl):
        self.clients.remove(cl)
        cl.close()
        self.messages_dic.pop((cl.connect_ip, cl.connect_port))
