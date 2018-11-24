"""

    This is the format of packets in our network:
    


                                                **ٔ  NEW Packet Format  **
     __________________________________________________________________________________________________________________
    | Version(1 Char/2 Bytes/1 Short Int)  |  Type(2 Chars/2 Bytes/1 Short Int)  |  Length(8 Chars/4 Bytes/1 Long Int) |
    |------------------------------------------------------------------------------------------------------------------|
    |                                  Source Server IP(12 Chars/8 Bytes/4 short Int)                                  |
    |------------------------------------------------------------------------------------------------------------------|
    |                                     Source Server Port(5 Chars/4 Bytes/1 Int)                                    |
    |------------------------------------------------------------------------------------------------------------------|
    |                                                    ..........                                                    |
    |                                                       BODY                                                       |
    |                                                    ..........                                                    |
    |__________________________________________________________________________________________________________________|

    for example:

    version = 1
    type = 02
    length = 00000012
    ip = '192.168.001.029'
    port = '06500'
    Body = 'Hello World!'

    Bytes = b'\x00\x01\x00\x02\x00\x00\x00\x0c\x00\xc0\x00\xa8\x00\x01\x00\x1d\x00\x00\x19dHello World!'
    String = 1020000001219216800102906500Hello World!


    Version:
        For now version is 1
    
    Type:
        01: Register
        02: Advertise
        03: Join
        04: Message
        05: Reunion
                e.g: type = '02' => advertise packet.
    Length:
        This field shows the character numbers for Body of the packet.

    Server IP/Port:
        We need this field for response packet in non-blocking mode.

    
    Packet descriptions:
    
        Register:
            Request:
        
                                 ** Body Format **
                 ________________________________________________
                |               REQ (3 Chars/3 Bytes)            |
                |------------------------------------------------|
                |        IP (12 Chars/8 Bytes/4 short Int)       |
                |------------------------------------------------|
                |          Port (5 Chars/4 Bytes/1 Int)          |
                |________________________________________________|
                
                For sending IP/Port of current node to the root to ask if it can register to network or not.
            Response:
        
                                 ** Body Format **
                 _________________________________________________
                |              RES (3 Chars/3 Bytes)              |
                |-------------------------------------------------|
                |              ACK (3 Chars/3 Bytes)              |
                |_________________________________________________|
                
                For now only should just send an 'ACK' from the root  to inform a node that it
                has been registered in the root if the 'Register Request' was successful.
                
        Advertise:
            Request:
            
                                ** Body Format **
                 ________________________________________________
                |              REQ (3 Chars/3 Bytes)             |
                |________________________________________________|
                
                Nodes for finding the IP/Port of their neighbour peer must send this packet to the root.
            Response:

                                ** Packet Format **
                 ________________________________________________
                |                RES(3 bytes)                    |
                |------------------------------------------------|
                |         Server IP (4*2 bytes/4 short Int)      |
                |------------------------------------------------|
                |          Server Port (4 bytes (1 Int))         |
                |________________________________________________|
                
                Root will response Advertise Request packet with sending IP/Port of the requester peer in this packet.
                
        Join:

                                ** Body Format **
                 ________________________________________________
                |             JOIN (4 Chars/4 Bytes)             |
                |________________________________________________|
            
            New node after getting Advertise Response from root must send this packet to specified peer 
            to tell him that they should connect together; When receiving this packet we should update our 
            Client Dictionary in Stream object.
            
            For next version Join packet must contain a field for validation the joining action.
            
        Message:
                                ** Body Format **
                 ________________________________________________
                |             Message (#Length Bytes)            |
                |________________________________________________|

            The message that want to broadcast to hole network. Right now this type only includes a plain text.
        
        Reunion:
            Hello:
        
                                ** Body Format **
                 ________________________________________________
                |             REQ (3 Chars / 3 Bytes)            |
                |------------------------------------------------|
                |    Number of Entries (2 Bytes(1 Short Int))    |
                |------------------------------------------------|
                |         IP0 (4*2 bytes/4 short Int)            |
                |------------------------------------------------|
                |              Port0 (4 bytes (1 Int))           |
                |------------------------------------------------|
                |         IP1 (4*2 bytes/4 short Int)            |
                |------------------------------------------------|
                |             Port1 (4 bytes (1 Int))            |
                |------------------------------------------------|
                |                     ...                        |
                |------------------------------------------------|
                |         IPN (4*2 bytes/4 short Int)            |
                |------------------------------------------------|
                |             PortN (4 bytes (1 Int))            |
                |________________________________________________|
                
                In every intervals (for now 20 seconds) peers must send this message to the root.
                Every other peers that received this packet should append their (ip, port) to 
                the packet and update Length.
            Hello Back:
        
                                    ** Body Format **
                 _______________________________________________________
                |                RES (3 Chars/3 bytes)                  |
                |-------------------------------------------------------|
                |   Number of Entries (2 Chars/2 Bytes/1 Short Int))    |
                |-------------------------------------------------------|
                |         IPN (12 Chars/8 Bytes/4 short Int)            |
                |-------------------------------------------------------|
                |             PortN (5 Chars/4 bytes/1 Int)             |
                |-------------------------------------------------------|
                |                           ...                         |
                |-------------------------------------------------------|
                |         IP1 (12 Chars/8 Bytes/4 short Int)            |
                |-------------------------------------------------------|
                |             Port1 5 Chars/4 bytes/1 Int)              |
                |_______________________________________________________|

                Root in answer of the Reunion Hello message will send this packet to the target node.
                In this packet all the nodes (ip, port) exist in order by path traversal to target.
            
    
"""
from struct import *


class Packet:
    def __init__(self, buf):
        print("Packet Constructor:\tbuffer: ", buf, " ,buffer type: ", type(buf))
        if type(buf) == bytes:
            buf = buf.decode("utf-8")
        print(buf)
        self._buf = buf
        self._header = buf[0:28]
        self._version = int(buf[0], 10)
        self._type = int(buf[1:3], 10)
        self._length = int(buf[3:11], 10)
        print("`len here: ", buf[3:11])
        self._source_server_ip = buf[11:26]
        self._source_server_port = buf[26:31]
        self._body = buf[31:]

    def get_header(self):
        """

        :return: Packet header
        :rtype: str
        """

        return self._header

    def get_version(self):
        """

        :return: Packet Version
        :rtype: int
        """
        return self._version

    def get_type(self):
        """

        :return: Packet type
        :rtype: int
        """
        return self._type

    def get_length(self):
        """

        :return: Packet length
        :rtype: int
        """
        return self._length

    def get_body(self):
        """

        :return: Packet body
        :rtype: str
        """
        return self._body

    def get_buf(self):
        """

        :return Packet buffer
        :return: str
        """

        packet = bytearray(self._length + 20)
        # print(packet)
        pack_into('!h', packet, 0, self._version)
        # print(packet)
        # print(unpack_from('!h', packet))

        pack_into('!h', packet, 2, self._type)
        # print(packet)
        # print(unpack_from('!hh', packet))

        pack_into('!l', packet, 4, self._length)
        # 10100023127.000.000.00119125REQ127.000.000.00119125
        # 112312700119125REQ127.000.000.00119125
        # 112312700119125REQ127.000.000.00119125
        ip_elements = [int(x) for x in self._source_server_ip.split('.')]
        pack_into('!hhhh', packet, 8, ip_elements[0], ip_elements[1], ip_elements[2], ip_elements[3])
        # print(packet)
        # print(unpack_from('!hhhhhh', packet))

        pack_into('!i', packet, 16, int(self._source_server_port))
        # print(packet)
        # print(unpack_from('!hhhhhhi', packet))
        # print(str(self._length))
        # print(str(self._body))
        fmt = str(int(self._length)) + 's'
        # print(fmt)
        # print(fmt)
        # print(pack('!' + fmt, body))
        pack_into('!' + fmt, packet, 20, self._body.encode('UTF-8'))
        # print(packet)
        # print(unpack_from('!hhlhhhhi' + fmt, packet))

        return packet

    def get_source_server_ip(self):
        """

        :return: Server IP address for sender of the packet.
        :rtype: str
        """
        return self._source_server_ip

    def get_source_server_port(self):
        """

        :return: Server Port address for sender of the packet.
        :rtype: str
        """
        return self._source_server_port

    def get_source_server_address(self):
        """

        :return: Server address; The format is like ('192.168.001.001', '05335').
        :rtype: tuple
        """

        return self.get_source_server_ip(), self.get_source_server_port()


class PacketFactory:

    @staticmethod
    def parse_buffer(buffer):

        """
        :param buffer: The buffer that should be parse to a validate packet format

        :return new packet
        :rtype Packet

        """

        print("before: ", buffer)
        version = str(unpack_from('!h', buffer)[0])
        print(version)
        type = str(unpack_from('!h', buffer, offset=2)[0]).zfill(2)
        print(type)
        length = str(int(unpack_from('!l', buffer, offset=4)[0]))
        print(length)
        ip = unpack_from('!hhhh', buffer, offset=8)
        print(ip)
        ip = str(ip[0]) + '.' + str(ip[1]) + '.' + str(ip[2]) + '.' + str(ip[3])
        ip = '.'.join(p.zfill(3) for p in ip.split('.'))

        print(ip)
        port = str(unpack_from('!i', buffer, offset=16)[0]).zfill(5)
        print(port)
        fmt = length + 's'
        print(fmt)
        body = unpack_from('!' + fmt, buffer, offset=20)[0].decode("utf-8")
        print(body)
        buffer = version + type + length.zfill(8) + ip + port + body
        print("after: ", buffer)

        return Packet(buf=buffer)

    @staticmethod
    def new_reunion_packet(type, source_address, nodes_array):
        """
        :param destination: (ip, port) of destination want to send reunion packet.
        :param nodes_array: [(ip0, port0), (ip1, port1), ...] It is the path to the 'destination'.

        :return New reunion packet.
        :rtype Packet

        """
        version = '1'
        packet_type = '05'
        if type == 'REQ':
            body = 'REQ'
        elif type == 'RES':
            body = 'RES'
        else:
            return None

        number_of_entity = str(len(nodes_array)).zfill(2)

        print("In new_reunion_packet: ", nodes_array)

        body = body + number_of_entity
        for (ip, port) in nodes_array:
            body = body + ip
            body = body + port
        length = str(len(body)).zfill(8)

        return Packet(version + packet_type + length + source_address[0] + source_address[1] + body)

    @staticmethod
    def new_advertise_packet(type, source_server_address, neighbor=None):
        """
        :param type: Type of Advertise packet
        :param source_server_address Server address of the packet sender.
        :param neighbor: The neighbor for advertise response packet; The format is like ('192.168.001.001', '05335').

        :type type: str
        :type source_server_address: tuple
        :type neighbor: tuple

        :return New advertise packet.
        :rtype Packet

        """
        print("Creating advertisement packet")
        version = '1'
        packet_type = '02'

        if type == 'REQ':
            body = 'REQ'
            length = '3'.zfill(8)
            print("Request adv packet created")
            return Packet(
                version + packet_type + length + source_server_address[0] + source_server_address[1].zfill(5) + body)

        elif type == 'RES':
            try:
                body = 'RES'
                body += neighbor[0]
                body += neighbor[1]
                length = '23'.zfill(8)

                print("Response adv packet created")
                return Packet(
                    version + packet_type + length + source_server_address[0] + source_server_address[1].zfill(
                        5) + body)
            except Exception as e:
                print(str(e))
                # print()
        else:
            raise Exception("Type is incorrect")

    @staticmethod
    def new_join_packet(source_server_address):
        """
        :param source_server_address: Server address of the packet sender.
        :type source_server_address: tuple

        :return New join packet.
        :rtype Packet

        """
        print("Creating join packet")
        version = '1'
        packet_type = '03'
        length = '4'.zfill(8)
        body = 'JOIN'

        return Packet(
            version + packet_type + length + source_server_address[0] + source_server_address[1].zfill(5) + body)

    @staticmethod
    def new_register_packet(type, source_server_address, address=(None, None)):
        """
        :param type: Type of Register packet
        :param source_server_address: Server address of the packet sender.
        :param address: If type is request we need address; The format is like ('192.168.001.001', '05335').

        :type type: str
        :type source_server_address: tuple
        :type address: tuple

        :return New Register packet.
        :rtype Packet

        """
        print("Creating register packet")
        version = "1"
        packet_type = "01"

        if type == "REQ":
            length = "23".zfill(8)
            body = "REQ" + '.'.join(str(int(part)).zfill(3) for part in source_server_address[0].split('.')) + \
                   str(source_server_address[1]).zfill(5)
            print("Request register packet created")
            print("Address for packet is: ", address)
        elif type == "RES":
            length = "6".zfill(8)
            body = "RESACK"
            print("Response register packet created")
        else:
            raise Exception("Irregular register type.")

        return Packet(
            version + packet_type + length + source_server_address[0] + source_server_address[1].zfill(5) + body)

        pass

    @staticmethod
    def new_message_packet(message, source_server_address):
        """
        Packet for sending a broadcast message to hole network.

        :param message: Our message
        :param source_server_address: Server address of the packet sender.

        :type message: str
        :type source_server_address: tuple

        :return: New Message packet.
        :rtype: Packet
        """
        version = '1'
        packet_type = '04'
        body = message
        length = str(len(message)).zfill(8)
        print("Message packet created")
        return Packet(
            version + packet_type + length + source_server_address[0] + source_server_address[1].zfill(5) + body)
