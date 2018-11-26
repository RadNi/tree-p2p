from src.tools.simpletcp.tcpserver import TCPServer
import threading

def echo(ip, queue, data):
    queue.put(bytes(input(data), 'utf8'))

server = TCPServer("000.000.000.000", 5353, echo)
# thr = threading.Thread(target=server.run)
# thr.start()
server.run()
print("done")