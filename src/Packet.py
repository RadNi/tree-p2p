"""

    This is the format of packets in our network:
    
                 ** Packet Format **
     ________________________________________________
    | Version(1 char)| Type(2 char) | Length(5 char) |
    |------------------------------------------------|
    |            Source Server IP(15 char)           |
    |------------------------------------------------|
    |           Source Server Port(5 char)           |
    |------------------------------------------------|
    |                      ....                      |
    |                      BODY                      |
    |                      ....                      |
    |________________________________________________|
    
    
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
        
                                ** Packet Format **
                 ________________________________________________
                |                       REQ                      |
                |------------------------------------------------|
                |                 IP (15 char)                   |
                |------------------------------------------------|
                |                 Port (5 char)                  |
                |________________________________________________|
                
                For sending IP/Port of current node to the root to ask if it can register to network or not.
            Response:
        
                                ** Packet Format **
                 ________________________________________________
                |                       RES                      |
                |------------------------------------------------|
                |                       ACK                      |
                |________________________________________________|
                
                For now only should just send an 'Ack' from the root  to inform a node that it 
                has been registered in the root if the 'Register Request' was successful.
                
        Advertise:
            Request:
            
                                ** Packet Format **
                 ________________________________________________
                |                      REQ                       |
                |________________________________________________|
                
                Nodes for finding the IP/Port of their neighbour peer must send this packet to the root.
            Response:

                                ** Packet Format **
                 ________________________________________________
                |                      RES                       |
                |------------------------------------------------|
                |             Server IP (15 char)                |
                |------------------------------------------------|
                |             Server Port (5 char)               |
                |________________________________________________|
                
                Root will response Advertise Request packet with sending IP/Port of the requester peer in this packet.
                
        Join:

                                ** Packet Format **
                 ________________________________________________
                |                     JOIN                       |
                |________________________________________________|
            
            New node after getting Advertise Response from root must send this packet to specified peer 
            to tell him that they should connect together; When receiving this packet we should update our 
            Client Dictionary in Stream object.
            
            For next version Join packet must contain a field for validation the joining action.
            
        Message:
                                ** Packet Format **
                 ________________________________________________
                |                     Message                    |
                |________________________________________________|

            The message that want to broadcast to hole network. Right now this type only includes a plain text.
        
        Reunion:
            Hello:
        
                                ** Packet Format **
                 ________________________________________________
                |                      REQ                       |
                |------------------------------------------------|
                |            Number of Entries(2 char)           |
                |------------------------------------------------|
                |                 IP0 (15 char)                  |
                |------------------------------------------------|
                |                 Port0 (5 char)                 |
                |------------------------------------------------|
                |                 IP1 (15 char)                  |
                |------------------------------------------------|
                |                 Port1 (5 char)                 |
                |------------------------------------------------|
                |                     ...                        |
                |------------------------------------------------|
                |                 IPN (15 char)                  |
                |------------------------------------------------|
                |                 PortN (5 char)                 |
                |________________________________________________|
                
                In every intervals (for now 20 seconds) peers must send this message to the root.
                Every other peers that received this packet should append their (ip, port) to 
                the packet and update Length.
            Hello Back:
        
                                ** Packet Format **
                 ________________________________________________
                |                      RES                       |
                |------------------------------------------------|
                |            Number of Entries(2 char)           |
                |------------------------------------------------|
                |                 IPN (15 char)                  |
                |------------------------------------------------|
                |                 PortN (5 char)                 |
                |------------------------------------------------|
                |                     ...                        |
                |------------------------------------------------|
                |                 IP1 (15 char)                  |
                |------------------------------------------------|
                |                 Port1 (5 char)                 |
                |________________________________________________|

                Root in answer of the Reunion Hello message will send this packet to the target node.
                In this packet all the nodes (ip, port) exist in order by path traversal to target.
            
    
"""


class Packet:

    def __init__(self, buf):
        print("Packet Constructor:\tbuffer: ",buf, " ,buffer type: ", type(buf) )
        if type(buf) == bytes:
            buf = buf.decode("utf-8")
        print(buf)
        self._buf = buf
        self._header = buf[0:28]
        self._version = int(buf[0], 10)
        self._type = int(buf[1:3], 10)
        self._length = int(buf[3:8], 10)
        self._source_server_ip = buf[8:23]
        self._source_server_port = buf[23:28]
        self._body = buf[28:]

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
        return self._buf

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

    def parse_buffer(self, buffer):

        """
        :param buffer: The buffer that should be parse to a validate packet format

        :return new packet
        :rtype Packet

        """

        return Packet(buf=buffer)

    def new_reunion_packet(self, type,  nodes_array):
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
        number_of_entity = str(len(nodes_array))
        if len(number_of_entity) < 2:
            number_of_entity = '0' + number_of_entity
        body = body + number_of_entity
        for (ip, port) in nodes_array:
            body = body + ip
            body = body + port
        length = str(len(body))
        while len(length) < 5:
            length = '0' + length
        return Packet(version + packet_type + length + body)

    def new_advertise_packet(self, type, source_server_address, neighbor=None):
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
            length = '00003'
            print("Request adv packtet created")
            return Packet(version + packet_type + length + source_server_address[0] + source_server_address[1] + body)

        elif type == 'RES':
            try:
                body = 'RES'
                body += neighbor[0]
                body += neighbor[1]
                length = '00023'
                print("Response adv packtet created")
                return Packet(
                    version + packet_type + length + source_server_address[0] + source_server_address[1] + body)
            except Exception as e:
                print(str(e))
        else:
            raise Exception("Type is incorrect")

    def new_join_packet(self, source_server_address):
        """
        :param source_server_address: Server address of the packet sender.
        :type source_server_address: tuple

        :return New join packet.
        :rtype Packet

        """
        print("Creating join packet")
        version = '1'
        packet_type = '03'
        length = '00004'
        body = 'JOIN'

        return Packet(version + packet_type + length + source_server_address[0] + source_server_address[1] + body)

    def new_register_packet(self, type, source_server_address, address=(None, None)):
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
            length = "00023"
            body = "REQ" + '.'.join(str(int(part)).zfill(3) for part in address[0].split('.')) + \
                   str(address[1]).zfill(5)
            print("Request register packet created")
        elif type == "RES":
            length = "00006"
            body = "RESACK"
            print("Response register packet created")
        else:
            raise Exception("Irregular register type.")

        return Packet(version + packet_type + length + source_server_address[0] + source_server_address[1] + body)

        pass

    def new_message_packet(self, message, source_server_address):
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
        length = str(len(message)).zfill(5)
        print("Message packet created")
        return Packet(version + packet_type + length + source_server_address[0] + source_server_address[1] + body)
