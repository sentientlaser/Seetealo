
import socket, sys

## required to allow the sockets to work on 2 and 3
_enc = lambda x: str(x)
_dec = lambda x: x
if sys.version_info[0] == 3:
    _enc = lambda x: bytes(x, 'utf-8')
    _dec = lambda x: str(x, 'utf-8')


## pasted, because it's easier than writing this and importing it.
## TODO: add async
def socket_listen(port, action, shutdown = None, consume_size = 16, shutdown_command = None):
    ''' listen on a TCP port
        port: the numerical port to listen on
        action: a function with prototype `action(conn, data)`
    '''

    if not shutdown_command:
        shutdown_command = _enc("!X")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        def consume():
            while True:
               conn, addr = sock.accept()
               try:
                   while True:
                       data = conn.recv(consume_size).strip()
                       if data:
                           if (data == shutdown_command):
                               conn.send(_enc('shutting down\n'))
                               return
                           action(conn, _dec(data))
                       else:
                           break
                   conn.send(_enc('done\n'))
               finally:
                   conn.close()
        sock.bind(('', int(port)))
        sock.listen(5)
        print("socket is listening on port ", port)
        consume()
    finally:
        sock.close()
        if shutdown: shutdown()

def socket_send(port, content):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', int(port)))
        sock.sendall(content.encode())
        sock.shutdown(socket.SHUT_WR)
        while True:
            data = sock.recv(4096)
            if not data:
                break
            print(_dec(data.strip()))
    finally:
        sock.close()
