from src.Stream import Stream
from src.Packet import Packet, PacketFactory


class Peer:

    def __init__(self, is_root=False):
        self._is_root = is_root
        #    TODO   here we should pass IP/Port of the Stream server to Stream constructor.
        self.stream = Stream()

        self.parent = None, None

        #   TODO    The arrival packets that should handle in future ASAP!
        self.packets = []
        self.neighbours = []

        self.packet_factory = PacketFactory()

        if self._is_root:
            self.network_nodes = []

        pass

    def user_interface(self):
        # Which the user or client sees and works with. run() #This method runs every time to
        #  see whether there is new messages or not.
        #   TODO
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
            self.stream.send_message(sender, p.get_buf())
        elif packet.get_body()[0:3] == "RES":
            ip = packet.get_body()[3:18]
            port = packet.get_body()[18:23]
            self.stream.add_client(ip, port)
            self.parent = (ip, port)
            join_packet = self.packet_factory.new_join_packet()
            self.stream.send_message(self.parent, join_packet.get_buf())
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
                self.stream.send_message((pbody[3:18], pbody[18:23]), res)
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
        pass

    def __handle_reunion_packet(self, packet, sender):
        pass

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
