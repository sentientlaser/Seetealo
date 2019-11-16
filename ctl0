#!/usr/bin/env python3
import sys
from blender.blender_ctl import *
from blender.gimp_ctl import *

app_name = sys.argv[1]

if (app_name == 'blender'):
    main = Blender().make_main_fn()
if (app_name == 'gimp'):
    main = Gimp().make_main_fn()
else:
    print("app `%s` is unkown" % app_name)
    sys.exit(1)



if __name__ == "__main__":
    main()
