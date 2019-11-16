
import threading, socket, sys, logging

fmt = '%(asctime)-16s %(levelname)-8s %(name)-30s %(message)s'
dtfmt = '%Y-%m-%d %H:%M'
logging.basicConfig(format=fmt, datefmt=dtfmt)

def getcustomlogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

## required to allow the sockets to work on 2 and 3
_enc = lambda x: str(x)
_dec = lambda x: x
if sys.version_info[0] == 3:
    _enc = lambda x: bytes(x, 'utf-8')
    _dec = lambda x: str(x, 'utf-8')


## pasted, because it's easier than writing this and importing it.
## TODO: add async
def socket_listen(port, action, shutdown = None, consume_size = 16, shutdown_command = None, async = False):
    socketslogger = getcustomlogger("socket server handler")
    ''' listen on a TCP port
        port: the numerical port to listen on
        action: a function with prototype `action(conn, data)`
    '''


    if not shutdown_command:
        shutdown_command = _enc("!X")

    def start():
        socketslogger.warn("starting server on port %s", port)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketslogger.debug("socket acquired %s", sock)
            sock.bind(('', int(port)))
            socketslogger.debug("socket bound to port %s", port)
            backlog = 5
            sock.listen(backlog)
            socketslogger.debug("socket listening, allowing %s backlogged connections", backlog)
            while True:
               conn, addr = sock.accept()
               socketslogger.info("socket is listening on port %s", port)
               try:
                   while True:
                       data = conn.recv(consume_size).strip()
                       socketslogger.debug("socket is listening on port %s", port)
                       if data:
                           if (data == shutdown_command):
                               conn.send(_enc('shutting down\n'))
                               return
                           action(conn, _dec(data))
                       else:
                           break
                   conn.send(_enc('command success\n'))
               except BaseException as x:
                   conn.send(_enc('command failure: %s\n', type(x).__name__))
                   raise x
               finally:
                   conn.close()
        finally:
            sock.close()
            if shutdown: shutdown()
            socketslogger.warn("shutting down server")

    if not async:
        socketslogger.warn("starting server in synchronous mode")
        start()
    else:
        socketslogger.warn("starting server in asynchronous mode")
        threading.Thread(target=start, args=(), name="server_thread", daemon = True).start()

def socket_send(port, content):
    socketslogger = getcustomlogger("socket client handler")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', port))
        socketslogger.debug("Connected to port %s", port)
        sock.sendall(content.encode())
        socketslogger.debug("sent '%s'", content.encode())
        sock.shutdown(socket.SHUT_WR)
        while True:
            data = sock.recv(4096)
            if not data:
                break
            socketslogger.info("recieved: '%s'", _dec(data.strip()))
    finally:
        sock.close()
        socketslogger.debug("connection closed")
