### PORT TO LISTEN ON
PORT = 9090

import sys, os, re, itertools        ### basic stuffW
from gimpfu import *

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shared', 'sockets.py')).read())

# detached from the plugin api so I can see if I can just run it as a startup script
def startup_server():
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
    socket_listen(PORT, onexportrequest, onshutdown)
