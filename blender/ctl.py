
import os
from shared.ctl import *
from blender.config import Config


class Blender:
    def __init__(this):
        this.config = Config()
        this.main = Main(this.config)
        this.pidfile = PidFile(this.config)
        this.sendsignal = SendSignal(this.config, this.pidfile)
        this.shutdownapp = ShutdownApp(this.config, this.pidfile, this.sendsignal)
        this.startupapp = StartupApp(this.config, this.pidfile, this.sendsignal)


    def startup(this, args = None):
        if not args: args = this.main.args()
        serverscript = this.main.relative(this.config.server_file)
        argpack = this.startupapp.pack(['--enable-autoexec', '--python', serverscript], args)
        this.startupapp.invoke(argpack)

    def shutdown(this):
        this.shutdownapp.invoke()

    def signal(this, args = None):
        if not args: args = this.main.args()
        sigpack = this.sendsignal.pack(this.config.signal_command_mappings)
        this.sendsignal.invoke(sigpack, args)

    def make_main_fn(this):
        return this.main.create({
            "startup"  : this.startup,
            "shutdown" : this.shutdown,
            "signal"   : this.signal
        })
