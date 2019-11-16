import os
from shared.app_ctl import *

class Config:
    def __init__(this):
        this.port = 9091
        this.app_name = 'blender'
        this.server_file = "blender/blender_ctl_server.py"
        this.signal_command_mappings = {'rltex':'R', 'export':'E'}

class Blender(AbstractApp):
    def __init__(this):
        AbstractApp.__init__(this, Config())
        this.startup_args = ['--enable-autoexec', '--python', this.serverscript]
