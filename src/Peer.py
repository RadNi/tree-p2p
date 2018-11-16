class Peer:

    def __init__(self):
        #TODO   add some initialisation here
        pass

    def stream(self):
        pass

    def user_interface(self):
        # Which the user or client sees and works with. run() #This method runs every time to
        #  see whether there is new messages or not.
        pass

    def packet_factory(self):
        pass

    def handle_packets(self):
        pass

    def run(self):
        pass

    def __handle_advertise_packet(self):
        pass

    def __handle_register_packet(self):
        pass

    def __handle_message_packet(self):
        pass

    def __handle_reunion_packet(self):
        pass


class Node:
    ip = str
    port = str
