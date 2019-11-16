#!/usr/bin/env python3

import os, threading, bpy

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'properties.py')).read())
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shared', 'sockets.py')).read())

def server_init():
    def reload_textures():
        for image in bpy.data.images:
            image.reload()
        for screen in bpy.data.screens: # can't use context when in a background thread.
            for area in screen.areas:
                if area.type in ['IMAGE_EDITOR', 'VIEW_3D']:
                    area.tag_redraw()

    def onrequest(conn, data):
        print("processing request", data)
        conn.send(bytes("data '%s'\n" % data, 'utf-8'))
        if data.upper() == 'R':
            reload_textures()

    def onshutdown():
        print("stopping export server on ", port())

    print("starting export server on ", port())
    socket_listen(port(), onrequest, onshutdown)

## Named `startup_server` to preserve consistency with other files
def startup_server():
    thread = threading.Thread(target=server_init, args=(), name="server_thread")
    thread.daemon = True
    thread.start()

startup_server()
