#!/usr/bin/env python2
import socket
import sys

### PORT TO LISTEN ON
PORT = 9090

def cmd(port, content):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', int(port)))
        sock.sendall(content.encode())
        sock.shutdown(socket.SHUT_WR)
        while True:
            data = sock.recv(4096)
            if not data:
                break
            print  data.strip()
    finally:
        sock.close()


def cmdstr():
    if 'exit' in sys.argv:
        return '!X'
    else:
        cmdstr = ''
        if 'save' in sys.argv:
            cmdstr += 'S'
        if 'export' in sys.argv:
            cmdstr += 'E'
        return cmdstr

cmd(PORT, cmdstr())
