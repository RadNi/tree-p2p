from src.tools.simpletcp.tcpserver import TCPServer


def echo(ip, queue, data):
    queue.put(bytes(input(data), 'utf8'))

server = TCPServer("localhost", 5050, echo)
server.run()
