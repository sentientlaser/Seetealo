#!/usr/bin/env python3
import socket
import sys, os, subprocess

import psutil

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
            print(str(data.strip(), 'utf-8'))
    finally:
        sock.close()


def msgstr():
    if 'stop' in sys.argv:
        return '!X'
    else:
        cmdstr = ''
        if 'save' in sys.argv:
            cmdstr += 'S'
        if 'export' in sys.argv:
            cmdstr += 'E'
        return cmdstr

def main():
    cmdstr = sys.argv[1]
    filepath = os.path.dirname(os.path.abspath(__file__))
    pidfilepath = os.path.join(filepath, ".gimp.pid")

    if cmdstr == 'startup':
        serverfilepath = os.path.join(filepath, "gimp-ctl-server.py")
        print(serverfilepath)
        batch_cmd = 'exec(open("%s").read()); startup_server();' % serverfilepath
        print(batch_cmd)
        if os.path.isfile(pidfilepath):
            print("gimp pid file exists, either delete it or use the `shutdown` command")
            return
        baseargs = [
            'gimp',
            '--batch-interpreter=python-fu-eval',
            '-b',
            batch_cmd
            ]
        suppliedargs = []
        for arg in list(sys.argv[2:]):
            suppliedargs += [os.path.expanduser(arg)]
        proc = subprocess.Popen(baseargs+suppliedargs)
        with open(pidfilepath, "w") as pidfile:
            pidfile.write(str(proc.pid))
    elif cmdstr == 'shutdown':
        try:
            with open(pidfilepath, "r") as pidfile:
                pid = int(pidfile.read())
            proc = psutil.Process(pid)
            cmd(PORT, '!X')
            for child in proc.children(recursive=True):  # or parent.children() for recursive=False
                child.kill()
            proc.kill()
        except psutil.NoSuchProcess:
            print("no gimp process detected... just clening up")
        finally:
            os.remove(pidfilepath)
    elif cmdstr == 'send' :
        cmd(PORT, msgstr())

if __name__ == "__main__":
    main()
