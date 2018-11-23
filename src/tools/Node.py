from src.tools.simpletcp.clientsocket import ClientSocket


class Node:
    def __init__(self, server_address, set_root=False, set_register=False):
        """

        :param server_address: Nodes server address.
        """

        self.server_ip = Node.parse_ip(server_address[0])
        self.server_port = Node.parse_port(server_address[1])

        print( "                    inja, ", self.server_port)
        print(server_address)

        self.out_buff = []
        self.is_root = set_root
        self.is_register_connection = set_register

        try:
            self.client = ClientSocket(self.server_ip, int(self.server_port, 10), single_use=False)
        except:
            print("Node was detached.")
            self.out_buff.clear()

    def send_message(self):
        """
        Final function to send buffer to the clients socket.

        :return:
        """
        # print("in sending message: ", self.out_buff)
        for b in self.out_buff:
            print("In sending message buffer: ", b)
            # print(b)
            response = self.client.send(b)

            print("Response: ", response, " ", type(response))
            if response != b'ACK':
                print("The ", self.get_server_address()[0], ": ", self.get_server_address()[1],
                      " did not response with b'ACK'. ", response)

        self.out_buff.clear()

    def add_message_to_out_buff(self, message):
        """
        Here we will add new message to the server out_buff, then in 'send_message' will send them.

        :param message: The message we want to add to out_buff
        :return:
        """
        self.out_buff.append(message)

    def close(self):
        """
        Closing client object.
        :return:
        """
        self.client.close()

    def get_server_address(self):
        """

        :return: Server address in a pretty format.
        :rtype: tuple
        """
        return self.server_ip, self.server_port

    def get_standard_server_address(self):
        """

        :return: Server address in standard format.
        :rtype: tuple
        """

        port_prime = int(self.server_port)

        return self.server_ip, port_prime

    @staticmethod
    def parse_ip(ip):
        """
        Automatically change the input IP format like '192.168.001.001'.
        :param ip: Input IP
        :type ip: str

        :return: Formatted IP
        :rtype: str
        """
        return '.'.join(str(int(part)).zfill(3) for part in ip.split('.'))

    @staticmethod
    def parse_port(port):
        """
        Automatically change the input IP format like '05335'.
        :param port: Input IP
        :type port: str

        :return: Formatted IP
        :rtype: str
        """
        return str(int(port)).zfill(5)

