#!/usr/bin/env python3

import os, bpy, logging

def port():
    return 9091

serverscript = os.path.dirname(os.path.abspath(__file__))
serverscript =  os.path.dirname(serverscript)
serverscript =  os.path.join(serverscript, 'shared', 'serverctl.py')
exec(open(serverscript, "r").read())

blenderctlsrvlogger = getcustomlogger('gimp control server')

def reload_textures(conn):
    for image in bpy.data.images:
        image.reload()
        conn.send(_enc("reloaded image '%s'\n" % image.name))
    for screen in bpy.data.screens: # can't use context when in a background thread.
        for area in screen.areas:
            if area.type in ['IMAGE_EDITOR', 'VIEW_3D']:
                area.tag_redraw()
    conn.send(_enc("refreshed screens\n"))

def save_file(conn):
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    conn.send(_enc("saved blend '%s'\n" % bpy.data.filepath))


def export_fdx(conn):
    bpy.ops.export_scene.fbx(axis_forward='Z', axis_up='Y')
    print("TBD")


def onrequest(conn, data):
    blenderctlsrvlogger.debug("processing texture reload")
    conn.send(_enc("processing request '%s'\n" % data))
    if 'R' in data.upper():
        blenderctlsrvlogger.debug("processing texture reload")
        reload_textures(conn)
    if 'S' in data.upper():
        blenderctlsrvlogger.debug("processing save file")
        save_file(conn)
    if 'E' in data.upper():
        blenderctlsrvlogger.debug("processing export")
        export_fdx(conn)



blenderctlsrvlogger.info("starting export server on %s", port())
socket_listen(port(), onrequest, async = True)
