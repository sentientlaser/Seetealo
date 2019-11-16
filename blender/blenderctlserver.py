#!/usr/bin/env python3

import os, bpy, logging

def port():
    return 9091

serverscript = os.path.dirname(os.path.abspath(__file__))
serverscript =  os.path.dirname(serverscript)
serverscript =  os.path.join(serverscript, 'shared', 'serverctl.py')
exec(open(serverscript, "r").read())

blenderctlsrvlogger = getcustomlogger('gimp control server')

def reload_textures():
    for image in bpy.data.images:
        image.reload()
    for screen in bpy.data.screens: # can't use context when in a background thread.
        for area in screen.areas:
            if area.type in ['IMAGE_EDITOR', 'VIEW_3D']:
                area.tag_redraw()

def onrequest(conn, data):
    conn.send(_enc("processing request '%s'\n" % data))
    if data.upper() == 'R':
        reload_textures()


blenderctlsrvlogger.info("starting export server on %s", port())
socket_listen(port(), onrequest, async = True)