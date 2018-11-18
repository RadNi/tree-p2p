# implementation of Packet and PacketFactory classes
# packetFactory


class PacketFactory:

    def parse_buffer(self, buffer):

        """
        :param buffer: The buffer that should be parse to a validate packet format
        :return packet

        """
        pass

    def new_reunion_packet(self, destination, nodes_array):
        """
        :param destination: (ip, port) of destination want to send reunion packet.
        :param nodes_array: [(ip0, port0), (ip1, port1), ...] It is the path to the 'destination'.

        :return new reunion packet.

        """
        pass

    def new_advertise_packet(self):
        """
        :param buffer:

        """
        pass

    def new_register_packet(self):
        # make a new register packet.
        pass


"""

    This is the format of packets in our network:
    
                 ** Packet Format **
     ________________________________________________
    | Version(1 char)| Type(2 char) | Length(5 char) |
    |------------------------------------------------|
    |                      ....                      |
    |                      BODY                      |
    |                      ....                      |
    |________________________________________________|
    
    
    Version:
        For now version is 1
    
    Type:
        1: Register
        2: Advertise
        3: Join
        4: Message
        5: Reunion
        
    Length:
        This field shows the character numbers for Body of the packet.
        
    
    Packet descriptions:
    
        Register:
            Request:
        
                                ** Packet Format **
                 ________________________________________________
                |                 IP (15 char)                   |
                |------------------------------------------------|
                |                 Port (5 char)                  |
                |________________________________________________|
                
                For sending IP/Port of current node to the root to ask if it can register to network or not.
            Response:
        
                                ** Packet Format **
                 ________________________________________________
                |                       ACK                      |
                |________________________________________________|
                
                
                For now only should just send an 'Ack' from the root  to inform a node that it 
                has been registered in the root if the 'Register Request' was successful.
                
        Advertise:
            Request:
                Nodes for finding the IP/Port of their neighbour peer must send this packet to the root.
            Response:
                Root will response Advertise Request packet with sending IP/Port of the requester peer in this packet.
                
        Join:
            New node after getting Advertise Response from root must send this packet to specified peer 
            to tell him that they should connect together; When receiving this packet we should update our 
            Client Dictionary in Stream object.
            
        Message:
            The message that want to broadcast to hole network. Right now this type only includes a plain text.
        
        Reunion:
            Hello:
                In every intervals (for now 20 seconds) peers must send this message to the root.
                Every other peers that received this packet should append their (ip, port) to 
                the packet and update Length.
            Hello Back:
                Root in answer of the Reunion Hello message will send this packet to the target node.
                In this packet all the nodes (ip, port) exist in order by path traversal to target.
            
    
"""


class Packet:

    def __init__(self, buf):
        self.header = buf
        self.version = int(buf[0], 10)
        self.type = int(buf[1:3], 10)
        self.length = int(buf[3:8], 10)
        self.body = buf[8:]

    def get_header(self):
        """

        :return: Packet header
        :rtype: String
        """

        return self.header

    def get_version(self):
        """

        :return: Packet Version
        :rtype: Integer
        """
        return self.version

    def get_type(self):
        """

        :return: Packet type
        :rtype: Integer
        """
        return self.type

    def get_length(self):
        """

        :return: Packet length
        :rtype: Integer
        """
        return self.length

    def get_body(self):
        """

        :return: Packet body
        :rtype: String
        """
        return self.body
