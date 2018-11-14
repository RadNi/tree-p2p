# implementation of Packet and PacketFactory classes
# packetFactory


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


class Node:
    ip = str
    port = str


class Packet:
    type = str
    header = str
    body = str
    node = Node()


class Reunion(Packet):

    def get_destination(self):
        pass


class RegisterRequest:
    ack = str


class RegisterResponse:
    ip = str
    port = str


class Message(Packet):
    plain_text = str


class Advertise(Packet):
    ip = str
    port = str
