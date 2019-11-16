import os
from shared.appctl import *
from shared.serverctl import getcustomlogger


class Config:
    def __init__(this):
        this.port = 9091
        this.app_name = 'blender'
        this.server_file = "blender/blenderctlserver.py"
        this.signal_command_mappings = {'rltex':'R', 'export':'E'}
        this.logger = getcustomlogger('blender control')

class Blender(AbstractApp):
    def __init__(this):
        AbstractApp.__init__(this, Config())
        this.startup_args = ['--enable-autoexec', '--python', this.serverscript]
