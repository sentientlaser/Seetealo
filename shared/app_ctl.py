
import sys, os, subprocess, psutil
from shared.sockets import socket_send

class AbstractApp:
    def __init__(this, config):
        this.config = config
        this.main = Main(this.config)
        this.pidfile = PidFile(this.config)
        this.sendsignal = SendSignal(this.config, this.pidfile)
        this.shutdownapp = ShutdownApp(this.config, this.pidfile, this.sendsignal)
        this.startupapp = StartupApp(this.config, this.pidfile, this.sendsignal)
        this.serverscript = this.main.relative(this.config.server_file)
        this.startup_args = []


    def startup(this, args = None):
        if not args: args = this.main.args()
        argpack = this.startupapp.pack(this.startup_args, args)
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

class Main:
    def __init__(this, config):
        this.config = config

    @staticmethod
    def filepath():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # XXX: Can be bittle `/usr/bin` -> '/usr' but `/usr/bin/` - '/usr/bin'

    def relative(this, path):
        return os.path.join(Main.filepath(), path) # XXX: This shoudl fix any brittleness in the filepath

    #TODO: make this a static property
    def command(this):
        try:
            return sys.argv[2]
        except IndexError:
            raise ValueError("Command not supplied")

    #TODO: make this a static property
    def args(this):
        return sys.argv[3:]

    def create(this, cmd_dict):
        def fn():
            if not this.command() in cmd_dict: raise ValueError("command %s not understood,  options are %s" % (this.command(), cmd_dict.keys()))
            for cmd in cmd_dict:
                if cmd == this.command():
                    command = cmd_dict[cmd]
                    command()
        return fn

class PidFile:

    negate = lambda x: not x
    identity = lambda x: x ## should never need this, it's just to make use PidFile.check is only called with this or 'negate'

    def __init__(this, config):
        this.config = config

    #TODO: make this a static property
    def path(this):
        return os.path.join(Main.filepath(), ".%s.pid" % this.config.app_name)

    def exists(this):
        return os.path.exists(this.path()) and os.path.isfile(this.path())

    def check(this, msg, negate_fn = identity):
        if not negate_fn in [PidFile.negate, PidFile.identity]: raise ValueError("only identity or negate may be passed to check")
        if negate_fn(this.exists()):
            raise EnvironmentError(msg)
        return True

    def get(this):
        with open(this.path(), "r") as pidfile_handle:
            return int(pidfile_handle.read())

    def set(this, pid):
        with open(this.path(), "w") as pidfile_handle:
            pidfile_handle.write(str(pid))

    def remove(this):
        if this.exists(): os.remove(this.path())

class SendSignal:

    def __init__(this, config, pidfile):
        this.config = config
        this.pidfile = pidfile

    def pack(this, sig_dict):
        def fn(args):
            if 'stop' in args:
                return '!X'
            else:
                signal = ''
                for key in sig_dict:
                    if key in args:
                        signal += sig_dict[key]
                if len(signal) == 0: raise ValueError("Unknown signal set %s" % args)
                return signal
        return fn

    def invoke(this, pack_signal_fn, args):
        print(pack_signal_fn(args))
        this.pidfile.check("pid file not found, please start %s" % this.config.app_name, PidFile.negate)
        socket_send(this.config.port, pack_signal_fn(args))

    def stop(this):
        socket_send(this.config.port, '!X')


class ShutdownApp:

    def __init__(this, config, pidfile, sendsignal):
        this.config = config
        this.pidfile = pidfile
        this.sendsignal = sendsignal

    def invoke(this):
        this.pidfile.check("no pid file for %s found, nothing to do" % this.config.app_name, PidFile.negate)
        try:
            try:
                this.sendsignal.stop()
            except ConnectionRefusedError as e:
                print("Server not running, skipping")
            proc = psutil.Process(this.pidfile.get())
            for child in proc.children(recursive=True):
                child.kill()
            proc.kill()
        except psutil.NoSuchProcess:
            print("no %s process detected... just cleaning up" % this.config.app_name)
        finally:
            this.pidfile.remove()

class StartupApp:

    def __init__(this, config, pidfile, sendsignal):
        this.config = config
        this.pidfile = pidfile
        this.sendsignal = sendsignal

    def start(this, cmd_arr):
        proc = subprocess.Popen([this.config.app_name] + cmd_arr)
        this.pidfile.set(proc.pid)

    def pack(this, flags, files):
        def fn():
            return flags + list(map(lambda x: os.path.expanduser(x), files))
        return fn

    def invoke(this, pack_cmdline_fn):
        # TODO: send a ping?
        this.pidfile.check("pid file exists, either delete it or use the `shutdown` command")
        this.start(pack_cmdline_fn())
