from src.Stream import Stream
from src.Packet import Packet, PacketFactory
from src.UserInterface import UserInterface
from src.tools.SemiNode import SemiNode
from src.tools.NetworkGraph import NetworkGraph, GraphNode
import time
import threading


"""
    Peer is our main object in this project.
    In this network Peers will connect together to make a tree graph.
    This network is not completely decentralised but will show you some real world challenges in Peer to Peer networks.
    
"""


class Peer:
    def __init__(self, server_ip, server_port, is_root=False, root_address=None):
        """
        The Peer object constructor.

        Code design suggestions:
            1. Initialise a Stream object for our Peer.
            2. Initialise a PacketFactory object.
            3. Initialise our UserInterface for interaction with user commandline.
            4. Initialise a Thread for handling reunion daemon.

        Warnings:
            1. For root Peer we need a NetworkGraph object.
            2. In root Peer start reunion daemon as soon as possible.
            3. In client Peer we need to connect to the root of the network, Don't forget to set this connection
               as a register_connection.


        :param server_ip: Server IP address for this Peer that should be pass to Stream.
        :param server_port: Server Port address for this Peer that should be pass to Stream.
        :param is_root: Specify that is this Peer root or not.
        :param root_address: Root IP/Port address if we are a client.

        :type server_ip: str
        :type server_port: int
        :type is_root: bool
        :type root_address: tuple
        """
        self._is_root = is_root

        self.stream = Stream(server_ip, server_port)

        self.parent = None

        self.packets = []
        self.neighbours = []
        self.flagg = True

        self.reunion_accept = True
        self.reunion_daemon_thread = threading.Thread(target=self.run_reunion_daemon)
        self.reunion_sending_time = time.time()
        self.reunion_pending = False

        self._user_interface = UserInterface()

        self.packet_factory = PacketFactory()

        if self._is_root:
            self.network_nodes = []
            self.registered_nodes = []
            self.network_graph = NetworkGraph(GraphNode((server_ip, str(server_port).zfill(5))))
            self.reunion_daemon_thread.start()
        else:
            self.root_address = root_address
            self.stream.add_node(root_address, set_register_connection=True)

    def start_user_interface(self):
        """
        For starting UserInterface thread.

        :return:
        """
        print("Starting UI")
        print('Available commands: ''Register', 'Advertise', 'SendMessage')

        self._user_interface.start()

    def handle_user_interface_buffer(self):
        """
        In every interval we should parse user command that buffered from our UserInterface.
        All of the valid commands are listed below:
            1. Register:  With this command client send a Register Request packet to the root of the network.
            2. Advertise: Send an Advertise Request to the root of the network for finding first hope.
            3. SendMessage: The following string will be add to a new Message packet and broadcast through network.

        Warnings:
            1. Ignore irregular commands from user.
            2. Don't forget to clear our UserInterface buffer.
        :return:
        """
        available_commands = ['Register', 'Advertise', 'SendMessage']
        #
        # print("user interface handler ", self._user_interface.buffer)
        for buffer in self._user_interface.buffer:
            if len(buffer) == 0:
                continue

            print('User interface handler buffer:', buffer)

            if buffer.split(' ', 1)[0] == available_commands[0]:
                # print("Handling buffer/register in UI")
                self.stream.add_message_to_out_buff(self.root_address,
                                                    self.packet_factory.new_register_packet("REQ",
                                                                                            self.stream.get_server_address(),
                                                                                            self.root_address).get_buf())
            elif buffer.split(' ', 1)[0] == available_commands[1]:
                # print("Handling buffer/advertise in UI")
                self.stream.add_message_to_out_buff(self.root_address,
                                                    self.packet_factory.new_advertise_packet("REQ",
                                                                                             self.stream.get_server_address()).get_buf())

            elif buffer.split(' ', 1)[0] == available_commands[2]:
                # print("Handling buffer/SendMessage in UI")
                self.send_broadcast_packet(self.packet_factory.new_message_packet(buffer.split(' ', 1)[1],
                                                                                  self.stream.get_server_address()).get_buf())
            else:
                print('Unknown Command!!!')
        self._user_interface.buffer = []

    def run(self):
        """
        Main loop of the program.

        Code design suggestions:
            1. Parse server in_buf of the stream.
            2. Handle all packets were received from our Stream server.
            3. Parse user_interface_buffer to make message packets.
            4. Send packets stored in nodes buffer of our Stream object.
            5. ** sleep the current thread for 2 seconds **

        Warnings:
            1. At first check reunion daemon condition; Maybe we have a problem in this time
               and so we should hold any actions until Reunion acceptance.
            2. In every situations checkout Advertise Response packets; even is Reunion in failure mode or not

        :return:
        """

        print("Running the peer...")
        while True:

            time.sleep(2)
            temp_array = self.stream.read_in_buf()

            if not self.reunion_accept:
                print("Reunion failure")

                for b in self.stream.read_in_buf():
                    # print("In main while: ", b)
                    p = self.packet_factory.parse_buffer(b)
                    # print("In for: ", p.get_type())
                    if p.get_type() == 2:
                        self.handle_packet(p)
                        temp_array.remove(b)
                        # self.stream.send_out_buf_messages(only_register=True)
                        break
                continue

            for b in temp_array:
                # print("In main while: ", b)
                p = self.packet_factory.parse_buffer(b)
                self.handle_packet(p)
                # self.packets.remove(p)
            self.stream.clear_in_buff()

            self.handle_user_interface_buffer()
            # print("Main while before user_interface handler")
            # self.send_broadcast_packets()
            self.stream.send_out_buf_messages()

    def run_reunion_daemon(self):
        """

        In this function we will handle all Reunion actions.

        Code design suggestions:
            1. Check if we are the network root or not; The actions are identical.
            2. If it's the root Peer, in every interval check the latest Reunion packet arrival time from every nodes;
               If time is over for the node turn it off (Maybe you need to remove it from our NetworkGraph).
            3. If it's a non-root peer split the actions by considering whether we are waiting for Reunion Hello Back
               Packet or it's the time to send new Reunion Hello packet.

        Warnings:
            1. If we are root of the network in the situation that want to turn a node off, make sure that you will not
               advertise the nodes sub-tree in our GraphNode.
            2. If we are a non-root Peer, save the time when you have sent your last Reunion Hello packet; You need this
               time for checking whether the Reunion was failed or not.
            3. For choosing time intervals you should wait until Reunion Hello or Reunion Hello Back arrival,
               pay attention that our NetworkGraph depth will not be bigger than 8. (Do not forget main loop sleep time)
            4. Suppose that you are a non-root Peer and Reunion was failed, In this time you should make a new Advertise
               Request packet and send it through your register_connection to the root; Don't forget to send this packet
               here, because in Reunion Failure mode our main loop will not work properly and everything will got stock!

        :return:
        """
        if self._is_root:
            while True:
                for n in self.network_graph.nodes:
                    if time.time() > n.latest_reunion_time + 36 and n is not self.network_graph.root:
                        print("We have lost a node!", n.address)
                        for child in n.children:
                            #   TODO    Turn all sub-tree off; not only children.
                            self.network_graph.turn_off_node(child.address)
                        self.network_graph.turn_off_node(n.address)
                        self.network_graph.remove_node(n.address)
                #   TODO    Handle this section
                time.sleep(2)

        else:
            while True:
                if not self.reunion_pending:
                    self.reunion_accept = True
                    time.sleep(4)
                    packet = self.packet_factory.new_reunion_packet("REQ", self.stream.get_server_address(),
                                                           [self.stream.get_server_address()])
                    self.stream.add_message_to_out_buff(self.parent.get_server_address(), packet.get_buf())
                    self.reunion_pending = True
                    self.reunion_sending_time = time.time()
                    self.flagg = True
                else:
                    if time.time() > self.reunion_sending_time+38 and self.flagg:

                        print("Ooops, Reunion was failed.")

                        self.reunion_accept = False
                        advertise_packet = self.packet_factory.new_advertise_packet("REQ", self.stream.get_server_address())
                        self.stream.add_message_to_out_buff(self.root_address, advertise_packet.get_buf())
                        self.flagg = False
                        self.stream.send_out_buf_messages(only_register=True)
                        # Reunion failed.
                        #   TODO    Make sure that parent will completely detach from our clients

    def send_broadcast_packet(self, broadcast_packet):
        """

        For setting broadcast packets buffer into Nodes out_buff.

        Warnings:
            1. Don't send Message packets through register_connections.

        :param broadcast_packet: The packet that should be broadcast through network.
        :type broadcast_packet: Packet

        :return:
        """

        for n in self.stream.nodes:
            # print(n.get_standard_server_address())
            # print(self.root_address)
            # if n.get_standard_server_address() != self.root_address:
            if not n.is_register_connection:
                self.stream.add_message_to_out_buff(n.get_server_address(), broadcast_packet)

    def handle_packet(self, packet):
        """

        This function act as a wrapper for other handle_###_packet methods to handle the packet.

        Code design suggestion:
            1.It's better to check packet validation right now; For example: Validation of the packet length.

        :param packet: The arrived packet that should be handled.

        :type packet Packet

        """
        if packet.get_length() != len(packet.get_body()):
            # print("packet.get_length() = ", packet.get_length(), packet.get_body(), packet.get_source_server_ip(),packet.get_source_server_port())
            return print('Packet Length is incorrect.')
        # print("Handling the packet...")
        if packet.get_version() == 1:
            if packet.get_type() == 1:
                self.__handle_register_packet(packet)
            elif packet.get_type() == 2:
                self.__handle_advertise_packet(packet)
            elif packet.get_type() == 3:
                self.__handle_join_packet(packet)
            elif packet.get_type() == 4:
                self.__handle_message_packet(packet)
            elif packet.get_type() == 5:
                self.__handle_reunion_packet(packet)
            else:
                print('Unexpected type:\t', packet.get_type())
                # self.packets.remove(packet)

    def __check_registered(self, source_address):
        """
        If the Peer is root of the network we need to find that is a node registered or not.

        :param source_address: Unknown IP/Port address.
        :type source_address: tuple

        :return:
        """

        for n in self.registered_nodes:
            if n.get_address() == source_address:
                return True
        return False

    def __handle_advertise_packet(self, packet):
        """
        For advertising peers in network, It is peer discovery message.

        Request:
            We should act as root of the network and reply with a neighbour address in a new Advertise Response packet.

        Response:
            When a Advertise Response packet type arrived we should update our parent peer and send a Join packet to the
            new parent.

        Code design suggestion:
            1. Start the Reunion daemon thread when the first Advertise Response packet received.
            2. When an Advertise Response message arrived  make a new Join packet immediately for advertised address.

        Warnings:
            1. Don't forget to ignore Advertise Request packets when you are non-root peer.
            2. The addresses which still haven't registered to the network can not request any peer discovery message.
            3. Maybe it's not the first time that source of the packet send Advertise Request message. This will happen
               in rare situations like Reunion Failure. Pay attention that don't advertise the address in packet sender
               sub-tree.
            4. When an Advertise Response packet arrived update our Peer parent for sending Reunion Packets.

        :param packet: Arrived register packet

        :type packet Packet

        :return:
        """

        # print("Handling advertisement packet...")

        if packet.get_body()[0:3] == 'REQ':
            if not self._is_root:
                # return print("Register request packet send to a non root node!")
                return

            # print("Packet is in Request type")

            if not self.__check_registered(packet.get_source_server_address()):
                # print(packet.get_source_server_address(), " trying to advertise before registering.")
                return

            # TODO Here we should check that is the node was advertised in past then update our GraphNode

            neighbor = self.__get_neighbour(packet.get_source_server_address())
            # print("Neighbor: \t", neighbor)
            p = self.packet_factory.new_advertise_packet(type='RES',
                                                         source_server_address=self.stream.get_server_address(),
                                                         neighbor=neighbor)

            server_address = packet.get_source_server_address()
            node = self.network_graph.find_node(server_address[0], server_address[1])

            if node is not None:
                self.network_graph.turn_on_node(server_address)
            #
            # else:
            #     self.network_graph.add_node(node, neighbor.address)
            #
            self.network_graph.add_node(server_address[0], server_address[1], neighbor)

            # print("We want to add this to the node: ", packet.get_source_server_address())
            self.network_nodes.append(SemiNode(packet.get_source_server_ip(), packet.get_source_server_port()))

            self.stream.add_message_to_out_buff(packet.get_source_server_address(), p.get_buf())
            # print()

        elif packet.get_body()[0:3] == 'RES':
            # print("Packet is in Response type")
            self.stream.add_node((packet.get_body()[3:18], packet.get_body()[18:23]))
            if self.parent:
                if self.stream.get_node_by_server(self.parent.server_ip, self.parent.server_port) in self.stream.nodes:
                    self.stream.remove_node(self.parent)
            self.parent = self.stream.get_node_by_server(packet.get_body()[3:18], packet.get_body()[18:23])

            addr = self.stream.get_server_address()
            join_packet = self.packet_factory.new_join_packet(addr)
            self.stream.add_message_to_out_buff(self.parent.get_server_address(), join_packet.get_buf())
            self.reunion_pending = False

            if not self.reunion_daemon_thread.isAlive():
                # print("Reunion thread started")
                self.reunion_daemon_thread.start()
        else:
            raise print('Unexpected Type.')

    def __handle_register_packet(self, packet):
        """
        For registration a new node to the network at first we should make a Node with stream.add_node for'sender' and
        save it.

        Code design suggestion:
            1.For checking whether an address is registered since now or not you can use SemiNode object except Node.

        Warnings:
            1. Don't forget to ignore Register Request packets when you are non-root peer.

        :param packet: Arrived register packet
        :type packet Packet
        :return:
        """
        # print("Handling register packet body: ", packet.get_body())
        pbody = packet.get_body()
        if pbody[0:3] == 'REQ':
            # print("Packet is in Request type")
            if not self._is_root:
                raise print('Register request packet send to a root node!')
            else:

                if self.__check_registered(packet.get_source_server_address()):
                    print(packet.get_source_server_address(), 'Trying to register again')
                    return

                res = self.packet_factory.new_register_packet(type='RES',
                                                              source_server_address=self.stream.get_server_address(),
                                                              address=self.stream.get_server_address())
                self.stream.add_node((packet.get_source_server_ip(), packet.get_source_server_port()),
                                     set_register_connection=True)
                # self.stream.add_client(pbody[3:18], pbody[18:23])
                self.registered_nodes.append(SemiNode(packet.get_body()[3:18], packet.get_body()[18:23]))
                self.stream.add_message_to_out_buff(packet.get_source_server_address(), res.get_buf())
                # self.stream.add_message_to_out_buf((pbody[3:18], pbody[18:23]), res)

        if pbody[0:3] == 'RES':
            print("Register Response sent")
            if pbody[3:6] == "ACK":
                print('ACK! Registered accomplished')
            else:
                raise Exception('Root did not send ack in the register response packet!')

    def __check_neighbour(self, address):
        """
        Checks is the address in our neighbours array or not.

        :param address: Unknown address

        :type address: tuple

        :return: Whether is address in our neighbours or not.
        :rtype: bool
        """
        if address in self.neighbours:
            return True
        print(self.parent.get_server_address(), " ", address)
        if address == self.parent.get_server_address():
            return True
        return False

    def __handle_message_packet(self, packet):
        """
        Only broadcast message to the other nodes.

        Warnings:
            1. Do not forget to ignore messages from unknown sources.
            2. Make sure that you are not sending a message to a register_connection.

        :param packet:

        :type packet Packet

        :return:
        """
        # print("Handling message packet...")
        # print("The message was just arrived is: ", packet.get_body(), " and source of the packet is: ",
        #       packet.get_source_server_address())
        new_packet = self.packet_factory.new_message_packet(packet.get_body(), self.stream.get_server_address())
        # for n in self.stream.nodes:
        #     print("From here:\t", n.get_server_address(), " ", n.is_register_connection)

        if not self.__check_neighbour(packet.get_source_server_address()):
            # print("The message is from an unknown source.")
            return

        for n in self.stream.nodes:
            if not n.is_register_connection:
                if n.get_server_address() != packet.get_source_server_address():
                    # print("Node considered to send message to: ", n.get_server_address())
                    self.stream.add_message_to_out_buff(n.get_server_address(), new_packet.get_buf())
                    print('Message sent to', n.get_server_address)

    def __handle_reunion_packet(self, packet):
        """
        In this function we should handle Reunion packet was just arrived.

        Reunion Hello:
            If you are root Peer you should answer with a new Reunion Hello Back packet.
            At first extract all addresses in the packet body and append them in descending order to the new packet.
            You should send the new packet to the first address in arrived packet.
            If you are a non-root Peer append your IP/Port address to the end of the packet and send it to your parent.

        Reunion Hello Back:
            Check that you are the end node or not; If not only remove your IP/Port address and send packet to the next
            address, otherwise you received your response from root and everything is fine.

        Warnings:
            1. Every time adding or removing an address from packet don't forget to update Entity Number field.
            2. If you are the root, update last Reunion Hello arrival packet from the sender node and turn it on.
            3. If you are the end node, update your Reunion mode from pending to acceptance.


        :param packet:
        :return:
        """
        # print("Handling reunion packet")
        if packet.get_body()[0:3] == "REQ":
            # print("Packet is in Request type")
            if self._is_root:
                number_of_entity = int(packet.get_body()[3:5])
                node_array = []
                ip_and_ports = packet.get_body()[5:]
                sender_ip = ip_and_ports[(number_of_entity - 1) * 20: (number_of_entity - 1) * 20 + 15]
                sender_port = ip_and_ports[(number_of_entity - 1) * 20 + 15: (number_of_entity - 1) * 20 + 20]
                for i in range(number_of_entity):
                    ip = ip_and_ports[i * 20:i * 20 + 15]
                    port = ip_and_ports[i * 20 + 15:i * 20 + 20]
                    node_array.insert(0, (ip, port))
                self.network_graph.turn_on_node(packet.get_source_server_address())
                node = self.network_graph.find_node(packet.get_source_server_ip(), packet.get_source_server_port())
                node.latest_reunion_time = time.time()
                p = self.packet_factory.new_reunion_packet(type='RES', source_address=self.stream.get_server_address(),
                                                           nodes_array=node_array)
                self.stream.add_message_to_out_buff((sender_ip, sender_port), p.get_buf())
            else:
                number_of_entity = int(packet.get_body()[3:5])
                node_array = []
                ip_and_ports = packet.get_body()[5:]
                for i in range(number_of_entity):
                    ip = ip_and_ports[i * 20:i * 20 + 15]
                    port = ip_and_ports[i * 20 + 15:i * 20 + 20]
                    node_array.append((ip, port))
                self_address = self.stream.get_server_address()
                node_array.append((self_address[0], self_address[1]))

                p = self.packet_factory.new_reunion_packet(type='REQ',
                                                           source_address=self.stream.get_server_address(),
                                                           nodes_array=node_array)
                parent_address = self.parent.get_server_address()
                self.stream.add_message_to_out_buff(parent_address, p.get_buf())
        elif packet.get_body()[0:3] == 'RES':
            # print("Packet is in Response type")
            number_of_entity = int(packet.get_body()[3:5])
            # print("Entity number is: ", number_of_entity)
            node_array = []
            ip_and_ports = packet.get_body()[5:]
            first_ip = ip_and_ports[0:15]
            first_port = ip_and_ports[15:20]
            self_address = self.stream.get_server_address()
            # print("Packet address: ", ip_and_ports[:20], ' address: ', self_address)

            if first_ip == self_address[0] and first_port == self_address[1]:

                if number_of_entity == 1:
                    print('Reunion Hello Back Packet Received')
                    self.reunion_pending = False
                    return

                sender_ip = ip_and_ports[20:35]
                sender_port = ip_and_ports[35:40]
                for i in range(1, number_of_entity):
                    ip = ip_and_ports[i * 20:i * 20 + 15]
                    port = ip_and_ports[i * 20 + 15:i * 20 + 20]
                    node_array.append((ip, port))
                p = self.packet_factory.new_reunion_packet(type='RES',
                                                           source_address=self.stream.get_server_address(),
                                                           nodes_array=node_array)
                self.stream.add_message_to_out_buff((sender_ip, sender_port), p.get_buf())
        else:
            raise print('Unexpected type')

    def __handle_join_packet(self, packet):
        """
        When a Join packet received we should add new node to our nodes array.
        In reality there is a security level that forbid joining every nodes to our network.

        :param packet: Arrived register packet.


        :type packet Packet

        :return:
        """
        print('Join packet sent')
        self.stream.add_node(packet.get_source_server_address())
        self.neighbours.append(packet.get_source_server_address())

        pass

    def __get_neighbour(self, sender):
        """
        Finds the best neighbour for the 'sender' from network_nodes array.
        This function only will call when you are a root peer.

        Code design suggestion:
            1.Use your NetworkGraph find_live_node to find the best neighbour.

        :param sender: Sender of the packet
        :return: The specified neighbor for the sender; The format is like ('192.168.001.001', '05335').
        """

        return self.network_graph.find_live_node(sender).address
