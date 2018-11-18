from src.tools.simpletcp.tcpserver import TCPServer

from src.tools.simpletcp.clientsocket import ClientSocket


class Stream:

    def __init__(self, ip, port):
        self.messages_dic = {}
        self.server_in_buf = {}
        self.parent = None

        def cb(ip, queue, data):
            queue.put(bytes('ACK'))
            # self.messages_dic.update({ip: self.messages_dic.get(ip).append(data)})
            self.server_in_buf.update({ip, data})

        self.server = TCPServer(ip, port, cb)
        self.clients = []

    def add_client(self, ip, port):
        if ip in self.messages_dic:
            #TODO
            return
        else:
            self.messages_dic.update({ip:[]})
            self.clients.append(ClientSocket(ip, port))


    def remove_client(self, cl):
        self.clients.remove(cl)
        cl.close()
        self.messages_dic.pop(cl.connect_ip)
    def remove_client_by_info(self, ip, port):
        rem_client = None
        for cl in self.clients:
            if cl.get_port() == port and cl.get_ip == ip:
                rem_client = cl
                break
        if rem_client != None:
            self.remove_client(rem_client)

    def read_in_buf(self):
        return self.server_in_buf

    def send_message(self, client, message):
        self.messages_dic.update({client, self.messages_dic.pop(client).append(message)})

    def set_parent(self, ip ,port):
        self.parent = ClientSocket(ip, port)
