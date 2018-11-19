from src.tools.simpletcp.tcpserver import TCPServer

from src.tools.simpletcp.clientsocket import ClientSocket


class Stream:

    def __init__(self, ip, port):
        """
        :param ip: 15 characters
        :param port: 5 characters
        """
        if not self.is_valid(ip, port):
            raise Exception("Invalid format of ip or port for TCPServer.")
            #   TODO    Error handling

        self.messages_dic = {}
        self.server_in_buf = {}
        # self.parent = None
        #   TODO    Parent should be in Peer object not here

        def cb(ip, queue, data):
            queue.put(bytes('ACK', 'utf8'))
            # self.messages_dic.update({ip: self.messages_dic.get(ip).append(data)})
            self.server_in_buf.update({ip, data})

        self.server = TCPServer(ip, port, cb)
        self.clients = []

    def add_client(self, ip, port):
        if not self.is_valid(ip, port):
            print("Invalid ip/port")
            return
        if (ip, port) in self.messages_dic:
            print("This client currently exists")
            return
        else:
            self.messages_dic.update({(ip, port): []})
            self.clients.append(ClientSocket(ip, port))

    def is_valid(self, ip, port):
        if len(str(ip)) != 15 or len(str(port)) != 5:
            return False
        return True

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
        if rem_client is not None:
            self.remove_client(rem_client)

    def read_in_buf(self):
        return self.server_in_buf

    def send_messages_to_client(self, client):
        """
        Send buffered messages to the 'client'

        :param client:
        :type client ClientSocket

        :return:
        """
        message = self.messages_dic.get(('.'.join(str(int(part)).zfill(3) for part in client.get_ip().split('.'))),
                                        client.get_port().zfill(5))

        response = client.send(message)

        if response.decode("UTF-8") != bytes('ACK'):
            print("The ", client.get_ip(), ": ", client.get_port(), " did not response with b'ACK'.")

    def send_out_buf_messages(self):
        """
        In this function we will send hole out buffers to their own clients.

        :return:
        """

        for c in self.clients:
            self.send_messages_to_client(c)
        
        # self.messages_dic.update({client, self.messages_dic.pop(client).append(message)})

    def add_message_to_out_buf(self, client, message):
        self.messages_dic.update({client, self.messages_dic.pop(client).append(message)})

    # def set_parent(self, ip ,port):
    #     if not self.is_valid(ip, port):
    #         print("Invalid ip/port")
    #         return
    #     self.parent = ClientSocket(ip, port)
