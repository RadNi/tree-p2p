# implementation of Packet and PacketFactory classes
# packetFactory
from src.Peer import Node


class PacketFactory:

    def parse_buffer(self):
        pass

    def new_reunion(self):
        pass

    def new_advertise_packet(self):
        # make a new advertise packet.
        pass

    def new_register_packet(self):
        # make a new register packet.
        pass


class Packet:
    type = str
    header = str
    body = str
    node = Node()


class Reunion(Packet):

    def get_destination(self):
        pass


class RegisterRequest(Packet):
    ack = str


class RegisterResponse(Packet):
    ip = str
    port = str


class Message(Packet):
    plain_text = str


class Advertise(Packet):
    ip = str
    port = str
