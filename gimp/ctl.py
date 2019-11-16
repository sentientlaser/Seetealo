import os
from shared.ctl import *

class Config:
    def __init__(this):
        this.port = 9090
        this.app_name = 'gimp'
        this.server_file = "gimp/gimp_ctl_server.py"
        this.signal_command_mappings = {'save':'S', 'export':'E'}

class Gimp(AbstractApp):
    def __init__(this):
        AbstractApp.__init__(this, Config())
        this.startup_args = [
            '--batch-interpreter=python-fu-eval',
            '-b', 'exec(open("%s").read()); startup_server();' % this.serverscript
            ]
