import os
from shared.appctl import *
from shared.serverctl import getcustomlogger

class Config:
    def __init__(this):
        this.port = 9090
        this.app_name = 'gimp'
        this.server_file = "gimp/gimpctlserver.py"
        this.signal_command_mappings = {'save':'S', 'export':'E'}
        this.logger = getcustomlogger('gimp control')

class Gimp(AbstractApp):
    def __init__(this):
        AbstractApp.__init__(this, Config())
        this.startup_args = [
            '--batch-interpreter=python-fu-eval',
            '-b', 'serverscript = "%s"; exec(open(serverscript).read())' % this.serverscript
            ]
