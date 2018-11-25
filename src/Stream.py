from src.tools.simpletcp.tcpserver import TCPServer

from src.tools.Node import Node
import threading


class Stream:

    def __init__(self, ip, port):
        """
        The Stream object constructor.

        Code design suggestion:
            1. Make a separate Thread for your TCPServer and start immediately.


        :param ip: 15 characters
        :param port: 5 characters
        """

        ip = Node.parse_ip(ip)
        port = Node.parse_port(port)

        self._server_in_buf = []

        def cb(ip, queue, data):
            queue.put(bytes('ACK', 'utf8'))
            # self.messages_dic.update({ip: self.messages_dic.get(ip).append(data)})
            self._server_in_buf.append(data)

        print("Binding server: ", ip, ": ", port)
        self._server = TCPServer(ip, int(port), cb)
        tcpserver_thread = threading.Thread(target=self._server.run)
        # self._server.run()
        tcpserver_thread.start()
        self.nodes = []
        self.ip = ip
        self.port = port

    def get_server_address(self):
        """

        :return: Our TCPServer address
        :rtype: tuple
        """
        return Node.parse_ip(self._server.ip), Node.parse_port(self._server.port)

    def clear_in_buff(self):
        """
        Discard any data in TCPServer input buffer.

        :return:
        """
        self._server_in_buf.clear()

    def add_node(self, server_address, set_register_connection=False):
        """
        Will add new node to our Stream.

        :param server_address: New node TCPServer address
        :param set_register_connection: Shows that is this connection a register_connection or not.

        :type server_address: tuple
        :type set_register_connection: bool

        :return:
        """
        node = Node(server_address, set_register=set_register_connection)

        self.nodes.append(node)

    def remove_node(self, node):
        """
        Remove a node from our Stream.

        Warnings:
            1. Close the node after deletion.

        :param node: The node we want to remove.
        :type node: Node

        :return:
        """
        self.nodes.remove(node)
        node.close()

    def get_node_by_server(self, ip, port):
        """

        Will find the node that has IP/Port address of input.

        Warnings:
            1. Before comparing the address parse it to a standard format with Node.parse_### functions.

        :param ip: input address IP
        :param port: input address Port

        :return: The node that input address.
        :rtype: Node
        """
        port = Node.parse_port(port)
        ip = Node.parse_ip(ip)
        for nd in self.nodes:
            if nd.get_server_address()[0] == ip and nd.get_server_address()[1] == port:
                return nd

    def add_message_to_out_buff(self, address, message):
        """
        In this function we will add message to the output buffer of the node that has the input address.
        Later we should use send_out_buf_messages to send these buffers into their sockets.

        :param address: Node address that we want to send message
        :param message: Message we want to send

        Warnings:
            1. Check whether the node address is in our nodes or not.

        :return:
        """
        print("add message to out buff: ", address, " ", message)
        n = self.get_node_by_server(address[0], address[1])
        # if n is None:
        #     n = self.get_node_by_client(address[0], address[1])
        if n is None:
            return print("Unexpected address to add message to out buffer.")

        n.add_message_to_out_buff(message)

    def read_in_buf(self):
        """
        Only returns the input buffer of our TCPServer.

        :return: TCPServer input buffer.
        :rtype: list
        """
        return self._server_in_buf

    def send_messages_to_node(self, node):
        """
        Send buffered messages to the 'node'

        Warnings:
            1. Insert an exception handler here; Maybe the node socket you want to send message has turned off and you
               need to remove this node from stream nodes.

        :param node:
        :type node Node

        :return:
        """

        try:
            node.send_message()
        except:
            self.remove_node(node)

    def send_out_buf_messages(self, only_register=False):
        """
        In this function we will send hole out buffers to their own clients.

        :return:
        """

        for n in self.nodes:
            if only_register:
                if n.is_register_connection:
                    self.send_messages_to_node(n)
            else:
                self.send_messages_to_node(n)
