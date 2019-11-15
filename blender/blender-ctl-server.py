#!/usr/bin/env python3

### PORT TO LISTEN ON
PORT = 9091

import sys, os, re, itertools        ### basic stuff
import socket                        ### networking
import threading, time               ### for thread control

import bpy
# exec(open("/home/daniel/Workspaces/3dModellingTest/ToolchainScripts/blender/refresher.py").read())


## pasted, because it's easier than writing this and importing it.
def listen(port, action, shutdown = None, consume_size = 16, escape_string= bytes("!X", 'utf-8')):
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

def server():
    def reload_textures():
        for image in bpy.data.images:
            image.reload()

        # can't use context when in a background thread.
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type in ['IMAGE_EDITOR', 'VIEW_3D']:
                    area.tag_redraw()

    def onrequest(conn, data):
        print("processing request", data)
        conn.send(bytes("data '%s'\n" % data, 'utf-8'))
        if data.upper() == 'R'
            reload_textures()

    def onshutdown():
        print("stopping export server on ", PORT)

    print("starting export server on ", PORT)
    listen(PORT, onrequest, onshutdown)


threading.Thread(target=server, args=(), name="server_thread").start() ## TODO: make daemon thread
