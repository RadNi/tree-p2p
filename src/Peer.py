from src.Stream import Stream
from src.Packet import Packet, PacketFactory
from src.UserInterface import UserInterface
from src.tools.SemiNode import SemiNode
from src.tools.NetworkGraph import NetworkGraph, GraphNode
import time
import random
import threading


class Peer:
    def __init__(self, server_ip, server_port, is_root=False, root_address=None):
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
        # Which the user or client sees and works with. run() #This method runs every time to
        #  see whether there is new messages or not.
        #   TODO
        print("Starting UI")
        self._user_interface.start()

        pass

    def handle_user_interface_buffer(self):
        """
        Only handle broadcast messages
        :return:
        """

        # print("user interface handler ", self._user_interface.buffer)
        for buffer in self._user_interface.buffer:
            if len(buffer) == 0:
                continue

            print("User interface handler buffer: ", buffer)

            if buffer[0] == '1':
                print("Handling buffer/1 in UI")
                self.stream.add_message_to_out_buff(self.root_address,
                                                    self.packet_factory.new_register_packet("REQ",
                                                                                            self.stream.get_server_address(),
                                                                                            self.root_address).get_buf())
            elif buffer[0] == '2':
                print("Handling buffer/2 in UI")
                self.stream.add_message_to_out_buff(self.root_address,
                                                    self.packet_factory.new_advertise_packet("REQ",
                                                                                             self.stream.get_server_address()).get_buf())

            elif buffer[0] == '4':
                print("Handling buffer/4 in UI")
                self.send_broadcast_packet(self.packet_factory.new_message_packet(buffer,
                                                                                      self.stream.get_server_address()).get_buf())
        self._user_interface.buffer = []

    def run(self):
        """
        Main loop of the program.
        The actions that should be done in this function listed below:

            1.Parse server in_buf of the stream.
            2.Handle all packets were received from server.
            3.Parse user_interface_buffer to make message packets.
            4.Send packets stored in nodes buffer of stream.
            5.** sleep for some milliseconds **

        :return:
        """

        print("Running the peer...")
        while True:

            time.sleep(2)
            temp_array = self.stream.read_in_buf()

            print("In while")

            if not self.reunion_accept:
                print("Reunion failure")

                for b in self.stream.read_in_buf():
                    # print("In main while: ", b)
                    p = self.packet_factory.parse_buffer(b)
                    print("In for: ", p.get_type())
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

        In this function we will handle all reunion actions.
        :return:
        """
        if self._is_root:
            while True:
                print("In reunion root daemon")
                for n in self.network_graph.nodes:
                    if time.time() > n.latest_reunion_time + 10 and n is not self.network_graph.root:
                        print("We have lost a node!", n.address)
                        for child in n.children:
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
                    if time.time() > self.reunion_sending_time+30 and self.flagg:

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

        In this function we will use the other handle_###_packet methods to handle the 'packet'.

        :param packet: The arrived packet that should be handled.

        :type packet Packet

        """
        if packet.get_length() != len(packet.get_body()):
            print("packet.get_length() = ", packet.get_length(), packet.get_body(), packet.get_source_server_ip(),packet.get_source_server_port())
            return print("Packet Length is incorrect.")
        print("Handling the packet...")
        if packet.get_version() == 1:
            print("Packet version:\t1")
            if packet.get_type() == 1:
                self.__handle_register_packet(packet)
            elif packet.get_type() == 2:
                print("Packet type:\t2")
                self.__handle_advertise_packet(packet)
            elif packet.get_type() == 3:
                print("Packet type:\t3")
                self.__handle_join_packet(packet)
            elif packet.get_type() == 4:
                print("Packet type:\t4")
                self.__handle_message_packet(packet)
            elif packet.get_type() == 5:
                print("Packet type:\t5")
                self.__handle_reunion_packet(packet)
            else:
                print("Unexpected type:\t", packet.get_type())
                # self.packets.remove(packet)

    def __check_registered(self, source_address):

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

        :param packet: Arrived register packet

        :type packet Packet

        :return:
        """

        print("Handling advertisement packet...")

        if packet.get_body()[0:3] == "REQ":
            if not self._is_root:
                raise print("Register request packet send to a non root node!")

            print("Packet is in Request type")

            if not self.__check_registered(packet.get_source_server_address()):
                print(packet.get_source_server_address(), " trying to advertise before registering.")
                return

            #TODO Here we should check that is the node was advertised in past then update our GraphNode

            neighbor = self.__get_neighbour(packet.get_source_server_address())
            print("Neighbor: \t", neighbor)
            p = self.packet_factory.new_advertise_packet(type="RES",
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

            print("We want to add this to the node: ", packet.get_source_server_address())
            self.network_nodes.append(SemiNode(packet.get_source_server_ip(), packet.get_source_server_port()))

            self.stream.add_message_to_out_buff(packet.get_source_server_address(), p.get_buf())

        elif packet.get_body()[0:3] == "RES":
            print("Packet is in Response type")
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
                print("Reunion thread started")
                self.reunion_daemon_thread.start()
        else:
            raise print("Unexpected Type.")

    def __handle_register_packet(self, packet):
        """
        For registration a new node to the network at first we should make a Node object for 'sender' and save it in
        nodes array.

        :param packet: Arrived register packet
        :type packet Packet
        :return:
        """
        print("Handling register packet body: ", packet.get_body())
        pbody = packet.get_body()
        if pbody[0:3] == "REQ":
            print("Packet is in Request type")
            if not self._is_root:
                raise print("Register request packet send to a root node!")
            else:

                if self.__check_registered(packet.get_source_server_address()):
                    print(packet.get_source_server_address(), " trying to register again")
                    return

                res = self.packet_factory.new_register_packet(type="RES",
                                                              source_server_address=self.stream.get_server_address(),
                                                              address=self.stream.get_server_address())
                self.stream.add_node((packet.get_source_server_ip(), packet.get_source_server_port()),
                                     set_register_connection=True)
                # self.stream.add_client(pbody[3:18], pbody[18:23])
                self.registered_nodes.append(SemiNode(packet.get_body()[3:18], packet.get_body()[18:23]))
                self.stream.add_message_to_out_buff(packet.get_source_server_address(), res.get_buf())
                # self.stream.add_message_to_out_buf((pbody[3:18], pbody[18:23]), res)
                #   TODO    Maybe in other time we should delete this node from our clients array.

        if pbody[0:3] == "RES":
            print("Packet is in Response type")
            if pbody[3:6] == "ACK":
                print("ACK! Registered accomplished")
            else:
                raise Exception("Root did not send ack in the register response packet!")

    def __check_neighbour(self, address):
        if address in self.neighbours:
            return True
        print(self.parent.get_server_address(), " ", address)
        if address == self.parent.get_server_address():
            return True
        return False

    def __handle_message_packet(self, packet):
        """
        For now only broadcast message to the other nodes.
        Do not forget to ignore messages from unknown sources.

        :param packet:

        :type packet Packet

        :return:
        """
        print("Handling message packet...")
        print("The message was just arrived is: ", packet.get_body(), " and source of the packet is: ",
              packet.get_source_server_address())
        new_packet = self.packet_factory.new_message_packet(packet.get_body(), self.stream.get_server_address())
        # for n in self.stream.nodes:
        #     print("From here:\t", n.get_server_address(), " ", n.is_register_connection)

        if not self.__check_neighbour(packet.get_source_server_address()):
            print("The message is from an unknown source.")
            return

        for n in self.stream.nodes:
            if not n.is_register_connection:
                if n.get_server_address() != packet.get_source_server_address():
                    print("Node considered to send message to: ", n.get_server_address())
                    self.stream.add_message_to_out_buff(n.get_server_address(), new_packet.get_buf())

        # if self.parent and self.parent.get_server_address() != packet.get_source_server_address():
        #     print("Node considered to send message to: ", self.parent.get_server_address())
        #     self.stream.add_message_to_out_buff(self.parent.get_server_address(), new_packet.get_buf())

    def __handle_reunion_packet(self, packet):
        """
        #TODO   @Ali complete doc please. :\

        :param packet:
        :return:
        """
        print("Handling reunion packet")
        if packet.get_body()[0:3] == "REQ":
            print("Packet is in Request type")
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
        elif packet.get_body()[0:3] == "RES":
            print("Packet is in Response type")
            number_of_entity = int(packet.get_body()[3:5])
            print("Entity number is: ", number_of_entity)
            node_array = []
            ip_and_ports = packet.get_body()[5:]
            first_ip = ip_and_ports[0:15]
            first_port = ip_and_ports[15:20]
            self_address = self.stream.get_server_address()
            print("Packet address: ", ip_and_ports[:20], ' address: ', self_address)

            if first_ip == self_address[0] and first_port == self_address[1]:

                if number_of_entity == 1:
                    print("Pending was changed")
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
            raise print("Unexpected type")

    def __handle_join_packet(self, packet):
        """
        When a Join packet received we should add new node to our nodes array.
        In future we should add a security level for this section to forbid joining without permission of network root.

        :param packet: Arrived register packet.
                       Latter we will use this for security.


        :type packet Packet

        :return:
        """
        print("Handling join packet...")
        self.stream.add_node(packet.get_source_server_address())
        self.neighbours.append(packet.get_source_server_address())

        pass

    def __get_neighbour(self, sender):
        """
        Finds the best neighbour for the 'sender' from network_nodes array.
        This function only will call when you are a root peer.

        :param sender: Sender of the packet
        :return: The specified neighbor for the sender; The format is like ('192.168.001.001', '05335').
        """

        # valid_nodes = []
        # for s in self.network_nodes:
        #     if s.get_address() != sender:
        #         valid_nodes.append(s)

        # if len(self.network_nodes) >= 1:
        #     #   TODO    add performance checking here.
        #     return random.choice(self.network_nodes).get_address()
        #
        # else:
        #     return self.stream.get_server_address()

        #   TODO @Ali it's your version, please fix this

        return self.network_graph.find_live_node(sender).address


