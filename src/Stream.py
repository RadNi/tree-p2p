from src.tools.simpletcp.tcpserver import TCPServer

from src.tools.Node import Node
import threading


class Stream:

    def __init__(self, ip, port):
        """
        :param ip: 15 characters
        :param port: 5 characters
        """
        if not self.is_valid(ip, port):
            raise Exception("Invalid format of ip or port for TCPServer.")
            #   TODO    Error handling

        self._server_in_buf = []
        # self.parent = None
        #   TODO    Parent should be in Peer object not here

        def cb(ip, queue, data):
            queue.put(bytes('ACK', 'utf8'))
            print("In callback: ", data)
            # self.messages_dic.update({ip: self.messages_dic.get(ip).append(data)})
            self._server_in_buf.append(data)

        print("Binding server: ", ip, ": ", port)
        self._server = TCPServer(ip, port, cb)
        tcpserver_thread = threading.Thread(target=self._server.run)
        # self._server.run()
        tcpserver_thread.start()
        self.nodes = []
        self.ip = ip
        self.port = port

    def get_server_address(self):
        return Node.parse_ip(self._server.ip), Node.parse_port(self._server.port)

    def clear_in_buff(self):
        self._server_in_buf = []

    def add_node(self, server_address, set_register_connection=False):
        # node = None
        # try:
        node = Node(server_address, set_register=set_register_connection)
        # except:
        #     print("Node was detached.")
        #     # self.remove_node()
        # if node is not None:
        self.nodes.append(node)

    def is_valid(self, ip, port):
        if len(str(ip)) != 15 or len(str(port)) > 5:
            return False
        return True

    def remove_node(self, node):
        self.nodes.remove(node)
        node.close()

    def get_node_by_server(self, ip, port):
        """

        :param ip:
        :param port:
        :return:
        :rtype: Node
        """
        port = Node.parse_port(port)
        ip = Node.parse_ip(ip)
        for nd in self.nodes:
            if nd.get_server_address()[0] == ip and nd.get_server_address()[1] == port:
                return nd

    def add_message_to_out_buff(self, address, message):
        print("add message to out buff: ", address, " ", message)
        n = self.get_node_by_server(address[0], address[1])
        # if n is None:
        #     n = self.get_node_by_client(address[0], address[1])
        if n is None:
            return print("Unexpected address to add message to out buffer.")

        n.add_message_to_out_buff(message)

    def read_in_buf(self):
        return self._server_in_buf

    def send_messages_to_node(self, node):
        """
        Send buffered messages to the 'node'

        :param node:
        :type node Node

        :return:
        """

        try:
            node.send_message()
        except:
            self.remove_node(node)

    def send_out_buf_messages(self):
        """
        In this function we will send hole out buffers to their own clients.

        :return:
        """

        for n in self.nodes:
            self.send_messages_to_node(n)
