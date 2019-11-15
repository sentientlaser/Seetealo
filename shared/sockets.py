
import socket

## pasted, because it's easier than writing this and importing it.
## TODO: add async
def socket_listen(port, action, shutdown = None, consume_size = 16, escape_string= bytes("!X", 'utf-8')):
    ''' listen on a TCP port
        port: the numerical port to listen on
        action: a function with prototype `action(conn, data)`
    '''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        def consume():
            while True:
               conn, addr = sock.accept()
               try:
                   while True:
                       data = conn.recv(consume_size).strip()
                       if data:
                           if (data == escape_string):
                               conn.send(bytes('shutting down\n', 'utf-8'))
                               return
                           action(conn, str(data, 'utf-8'))
                       else:
                           break
                   conn.send(bytes('done\n', 'utf-8'))
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
            print(str(data.strip(), 'utf-8'))
    finally:
        sock.close()
