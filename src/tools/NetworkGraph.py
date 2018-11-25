import time


class GraphNode:
    def __init__(self, address):
        """

        :param address: (ip, port)
        :type address: tuple

        """
        self.parent = None
        self.latest_reunion_time = time.time()
        self.children = []
        self.ip = address[0]
        self.port = address[1]
        self.address = address
        self.alive = False

    def set_parent(self, parent):
        self.parent = parent

    def set_address(self, new_address):
        self.address = new_address

    def __reset(self):
        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)


class NetworkGraph:
    def __init__(self, root):
        self.root = root
        root.alive = True
        self.nodes = [root]

    def find_live_node(self, sender):
        queue = [self.root]
        while len(queue) > 0:
            node = queue[0]
            number_of_live_children = 0
            if node.address is not sender:
                if self.find_node(sender[0], sender[1]) is not None:
                    if self.find_node(sender[0], sender[1]) is node:
                        continue
                    if self.find_node(sender[0], sender[1]).parent is not None:
                        if node is self.find_node(sender[0], sender[1]).parent:
                            continue
            else:
                continue
            for child in node.children:
                if child.alive:
                    number_of_live_children += 1
                    queue.append(child)
            if number_of_live_children < 2 and node.address is not sender:
                if self.find_node(sender[0], sender[1]) is not None:
                    if self.find_node(sender[0], sender[1]).parent is not None:
                        if node is not self.find_node(sender[0], sender[1]).parent:
                            return node
                    else:
                        return node
                else:
                    return node
            queue.pop(0)
        return self.root

    def find_node(self, ip, port):
        for node in self.nodes:
            if node.ip == ip and node.port == port:
                return node
        return None

    def turn_on_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        if node is not None:
            node.alive = True

    def turn_off_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        if node is not None:
            node.alive = False

    def remove_node(self, node_address):
        node = self.find_node(node_address[0], node_address[1])
        if node is not None:
            node.parent.children.remove(node)
            self.nodes.remove(node)

    def add_node(self, ip, port, father_address):
        father_node = self.find_node(father_address[0], father_address[1])
        new_node = self.find_node(ip, port)

        if new_node is None:
            new_node = GraphNode((ip, port))
            self.nodes.append(new_node)
        new_node.set_parent(father_node)
        father_node.add_child(new_node)
