from src.Stream import Stream
from src.Packet import Packet, PacketFactory
from src.UserInterface import UserInterface


class Peer:

    def __init__(self, is_root=False):
        self._is_root = is_root
        #    TODO   here we should pass IP/Port of the Stream server to Stream constructor.
        self.stream = Stream()

        self.parent = None, None

        #   TODO    The arrival packets that should handle in future ASAP!
        self.packets = []
        self.neighbours = []

        self._user_interface = UserInterface()

        self._user_interface_buffer = []

        self._broadcast_packets = []

        self.packet_factory = PacketFactory()

        if self._is_root:
            self.network_nodes = []

        pass

    def start_user_interface(self):
        # Which the user or client sees and works with. run() #This method runs every time to
        #  see whether there is new messages or not.
        #   TODO

        self._user_interface.start()

        pass

    def handle_user_interface_buffer(self):
        """
        Only handle broadcast messages
        :return:
        """

        for buffer in self._user_interface_buffer:
            self._broadcast_packets.append(self.packet_factory.new_message_packet(buffer))

    def run(self):
        """
        Main loop of the program.
        The actions that should be done in this function listed below:

            1.Parse server in_buf of the stream.
            2.Handle all packets were received from server.
            3.Parse user_interface_buffer to make message packets.
            4.Send packets stored in clients dictionary of stream.
            5.** sleep for some milliseconds **

        :return:
        """

        pass

    def handle_packet(self, packet, sender):
        """

        In this function we will use the other handle_###_packet methods to handle the 'packet'.

        :param packet: The arrived packet that should be handled.
        :param sender: The sender for packet; The format is like ('192.168.001.001', '05335').

        :type packet Packet
        :type sender tuple

        """
        if packet.get_length() != len(packet.get_body()):
            raise Exception("Packet Length is incorrect.")

        if packet.get_version() == 1:
            if packet.get_type() == 1:
                self.__handle_register_packet(packet, sender)
            elif packet.get_type() == 2:
                self.__handle_advertise_packet(packet, sender)
            elif packet.get_type() == 3:
                self.__handle_join_packet(packet, sender)
            elif packet.get_type() == 4:
                self.__handle_message_packet(packet, sender)
            elif packet.get_type() == 5:
                self.__handle_reunion_packet(packet, sender)

    def __handle_advertise_packet(self, packet, sender):
        """
        For advertising peers in network, It is peer discovery message.

        Request:
            We should act as root of the network and reply with a neighbour address in a new Advertise Response packet.

        Response:
            When a Advertise Response packet type arrived we should update our parent peer and send a Join packet to the
            new parent.

        :param packet: Arrived register packet
        :param sender: Sender of the 'packet'

        :type packet Packet
        :type sender tuple

        :return:
        """
        if packet.get_body()[0:3] == "REQ":
            p = self.packet_factory.new_advertise_packet(type="RES", neighbor=self.__get_neighbour(sender))
            self.stream.add_message_to_out_buf(sender, p.get_buf())
        elif packet.get_body()[0:3] == "RES":
            ip = packet.get_body()[3:18]
            port = packet.get_body()[18:23]
            self.stream.add_client(ip, port)
            self.parent = (ip, port)
            join_packet = self.packet_factory.new_join_packet()
            self.stream.add_message_to_out_buf(self.parent, join_packet.get_buf())
        else:
            raise Exception("Unexpected Type.")

    def __handle_register_packet(self, packet, sender):
        """
        For registration a new node to the network at first we should make a Node object for 'sender' and save it in
        nodes array.

        :param packet: Arrived register packet
        :param sender: Sender of the 'packet'
        :type packet Packet
        :type sender tuple
        :return:
        """
        pbody = packet.get_body()
        if pbody[0:3] == "REQ":
            if not self._is_root:
                raise Exception("Register request packet send to a non root node!")
            else:
                res = self.packet_factory.new_register_packet(type="RES")
                self.network_nodes.append(Node(pbody[3:18], pbody[18:23]))
                self.stream.add_client(pbody[3:18], pbody[18:23])
                self.stream.add_message_to_out_buf((pbody[3:18], pbody[18:23]), res)
                #   TODO    Maybe in some other time we should delete this client from our clients array.

        if pbody[0:3] == "RES":
            if pbody[3:6] == "ACK":
                print("Hooraa. We registered to the network.")
            else:
                raise Exception("Root did not send ack in the register response packet!")

    def __handle_message_packet(self, packet, sender):
        """
        For now only broadcast message to the other nodes.
        Do not forget to send message to the parent if exist.

        :param packet:
        :param sender:

        :type packet Packet
        :type sender tuple

        :return:
        """

        for c in self.stream.clients:
            if c != sender:
                self.stream.add_message_to_out_buf(c, packet.get_buf())

        if self.parent != sender:
            self.stream.add_message_to_out_buf(self.parent, packet.get_buf())

    def __handle_reunion_packet(self, packet):
        if packet.get_body()[0:3] == "REQ":
            if self._is_root:
                number_of_entity = int(packet.get_body()[0:2])
                node_array = []
                ip_and_ports = packet.get_body()[2:]
                sender_ip = ip_and_ports[(number_of_entity-1)*20 : (number_of_entity-1)*20 + 15]
                sender_port = ip_and_ports[(number_of_entity-1)*20 + 15 : (number_of_entity-1)*20 + 20]
                for i in range(number_of_entity):
                    ip = ip_and_ports[i*20:i*20+15]
                    port = ip_and_ports[i*20+15:i*21]
                    node_array.insert(0,(ip,port))

                sender = self.stream.get_client(ip= sender_ip, port= sender_port)
                p = self.packet_factory.new_reunion_packet(type='RES',nodes_array=node_array)
                self.stream.add_message_to_out_buf(sender,p.get_buf())
            else:
                number_of_entity = int(packet.get_body()[0:2])
                node_array = []
                ip_and_ports = packet.get_body()[2:]
                for i in range(number_of_entity):
                    ip = ip_and_ports[i * 20:i * 20 + 15]
                    port = ip_and_ports[i * 20 + 15:i * 21]
                    node_array.append((ip, port))
                node_array.append((self.stream.ip, self.stream.port))

                p = self.packet_factory.new_reunion_packet(type='REQ', nodes_array=node_array)
                self.stream.add_message_to_out_buf(self.parent, p.get_buf())
        elif packet.get_body()[0:3] == "RES":
            number_of_entity = int(packet.get_body()[0:2])
            node_array = []
            ip_and_ports = packet.get_body()[2:]
            first_ip = ip_and_ports[0:15]
            first_port = ip_and_ports[15:20]
            sender_ip = ip_and_ports[20:35]
            sender_port = ip_and_ports[35:40]
            if first_ip == self.stream.ip and first_port == self.stream.port:
                for i in range(number_of_entity-1):
                    ip = ip_and_ports[i * 20:i * 20 + 15]
                    port = ip_and_ports[i * 20 + 15:i * 21]
                    node_array.append((ip, port))
                sender = self.stream.get_client(ip=sender_ip, port= sender_port)
                p = self.packet_factory.new_reunion_packet(type='RES', nodes_array=node_array)
                self.stream.add_message_to_out_buf(sender, p.get_buf())
            else:
                raise Exception("Unexpected Ip or Port in Reunion's body")
        else:
            raise Exception("Unexpected type")




    def __handle_join_packet(self, packet, sender):
        """
        When a Join packet received we should add new node to our nodes array.
        In future we should add a security level for this section to forbid joining without permission of network root.

        :param packet: Arrived register packet.
                       Latter we will use this for security.

        :param sender: Sender of the 'packet'

        :type packet Packet
        :type sender tuple

        :return:
        """

        self.neighbours.append(sender)
        self.stream.add_client(sender[0], sender[1])

        pass

    def __get_neighbour(self, sender):
        """
        Finds the best neighbour for the 'sender' from network_nodes array.

        :param sender: Sender of the packet
        :return: The specified neighbor for the sender; The format is like ('192.168.001.001', '05335').
        """
        pass


class Node:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
