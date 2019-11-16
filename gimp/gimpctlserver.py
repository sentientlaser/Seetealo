### PORT TO LISTEN ON
PORT = 9090

import sys, os, re, itertools, logging, time
from gimpfu import *

#### Gimp isn't releasing the port correctly

socketscript = os.path.dirname(os.path.abspath(serverscript))  # serverscript is passed in on the command line via the python command
socketscript = os.path.join(os.path.dirname(socketscript), 'shared', 'serverctl.py')

execfile(socketscript)

gimpctlsrvlogger = getcustomlogger('gimp control server')

def onexportrequest(conn, data):
    conn.send("processing export server request signal %s" % data)

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

gimpctlsrvlogger.warn("starting export server on %s", PORT)
socket_listen(PORT, onexportrequest)
