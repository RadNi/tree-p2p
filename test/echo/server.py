from src.tools.simpletcp.tcpserver import TCPServer


def echo(ip, queue, data):
    queue.put(bytes(input(data), 'utf8'))

server = TCPServer("127.000.000.001", 5051, echo)
server.run()
