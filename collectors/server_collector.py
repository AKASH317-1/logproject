import socket
from queue import Queue

def start_server(log_queue: Queue):
    """
    Listens for UDP syslog messages on port 514 and pushes them into the queue.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 514))
    while True:
        data, addr = sock.recvfrom(65535)
        log_queue.put(("firewall", f"{addr} -> {data.decode()}"))