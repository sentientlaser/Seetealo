#!/usr/bin/env python2

### PORT TO LISTEN ON
PORT = 9090

import sys, os, re, itertools        ### basic stuff
import socket                        ### networking
import threading, time               ### for thread control
from gimpfu import *

## pasted, because it's easier than writing this and importing it.
def listen(port, action, shutdown = None, consume_size = 16, escape_string= "!X"):
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
                               conn.send('shutting down\n')
                               return
                           action(conn, data)
                       else: break
                   conn.send('done\n')
               finally:
                   conn.close()
        sock.bind(('', int(port)))
        sock.listen(5)
        print("socket is listening on port ", port)
        consume()
    finally:
        sock.close()
        if shutdown: shutdown()


def plugin_main(timg, tdrawable):
    def onexportrequest(conn, data):
        print("processing export server request", data)
        conn.send("data '%s'\n" % data)

        for image in gimp.image_list():
            filename = image.filename
            conn.send("processing file '%s'\n" % filename)
            if not filename:
                conn.send("skipped unnamed file\n")
                continue

            if not re.match(r".*\.xcf$", filename):
                conn.send("skipped non xcf file '%s'\n" % filename)
                continue

            if 'S' in data.upper():
                drawable = pdb.gimp_image_active_drawable(image)
                pdb.gimp_xcf_save(0, image, drawable, filename, filename)
                conn.send("saved file '%s'\n" % filename)

            if 'E' in data.upper():
                try:
                    filename_png = re.sub(r"xcf$", "png", filename)
                    pdb.gimp_selection_none(image)
                    pdb.gimp_edit_copy_visible(image)
                    image_png = pdb.gimp_edit_paste_as_new()
                    drawable_png = pdb.gimp_image_active_drawable(image_png)
                    pdb.file_png_save(image_png, drawable_png, filename_png, filename_png, 1, 9, 1, 1, 1, 1, 1)

                    conn.send("exported file '%s'\n" % filename_png)
                finally:
                    try:
                        pdb.gimp_image_delete(image_png)
                    except msg:
                        print(msg)

    def onshutdown():
        print("stopping export server on ", PORT)

    print("starting export server on ", PORT)
    listen(PORT, onexportrequest, onshutdown)


register(
        "export_server",
        "Saves and export all working files by listening to a socket",
        "Saves and export all working files by listening to a socket",
        "Daniel Bertinshaw",
        "Daniel Bertinshaw",
        "2019",
        "<Image>/Edit/Start Export Server",
        "RGB*, GRAY*",
        [],
        [],
        plugin_main)

main()
