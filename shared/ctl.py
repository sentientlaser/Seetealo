
import sys, os, subprocess, psutil

## TODO: makse these modules

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shared', 'sockets.py')).read())


class Main:
    #TODO: make this a static property
    @staticmethod
    def filepath():
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def relative(path):
        return os.path.join(Main.filepath(), path)

    #TODO: make this a static property
    @staticmethod
    def command():
        return sys.argv[1]

    #TODO: make this a static property
    @staticmethod
    def args():
        return sys.argv[2:]

    @staticmethod
    def create(cmd_dict):
        def fn():
            if not Main.command() in cmd_dict: raise ValueError("command %s not understood,  options are %s" % (Main.command()))
            for cmd in cmd_dict:
                if cmd == Main.command():
                    command = cmd_dict[cmd]
                    command()
        return fn

negate = lambda x: not x
identity = lambda x: x ## should never need this, it's just to make use PidFile.check is only called with this or 'negate'

class PidFile:

    #TODO: make this a static property
    @staticmethod
    def path():
        return os.path.join(Main.filepath(), ".%s.pid" % app_name())

    @staticmethod
    def exists():
        return os.path.exists(PidFile.path()) and os.path.isfile(PidFile.path())

    @staticmethod
    def check(msg, negate_fn = identity):
        if not negate_fn in [negate, identity]: raise ValueError("only identity or negate may be passed to check")
        if negate_fn(PidFile.exists()):
            raise EnvironmentError(msg)
        return True

    @staticmethod
    def get():
        with open(PidFile.path(), "r") as pidfile_handle:
            return int(pidfile_handle.read())

    @staticmethod
    def set(pid):
        with open(PidFile.path(), "w") as pidfile_handle:
            pidfile_handle.write(str(pid))

    @staticmethod
    def remove():
        if PidFile.exists(): os.remove(PidFile.path())

class ShutdownApp:
    @staticmethod
    def invoke():
        PidFile.check("no pid file for %s found, nothing to do" % app_name(), negate)
        try:
            proc = psutil.Process(PidFile.get())
            SendSignal.stop()
            for child in proc.children(recursive=True):
                child.kill()
            proc.kill()
        except psutil.NoSuchProcess:
            print("no %s process detected... just cleaning up" % app_name())
        finally:
            PidFile.remove()

class SendSignal:
    @staticmethod
    def pack(sig_dict):
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

    @staticmethod
    def invoke(pack_signal_fn, args):
        print(pack_signal_fn(args))
        PidFile.check("pid file not found, please start %s" % app_name(), negate)
        socket_send(port(), pack_signal_fn(args))

    @staticmethod
    def stop():
        socket_send(port(), '!X')

class StartupApp:
    @staticmethod
    def start(cmd_arr):
        proc = subprocess.Popen([app_name()] + cmd_arr)
        PidFile.set(proc.pid)

    @staticmethod
    def pack(flags, files):
        def fn():
            return [app_name()] + flags + list(map(lambda x: os.path.expanduser(x), files))
        return fn

    @staticmethod
    def invoke(pack_cmdline_fn):
        PidFile.check("pid file exists, either delete it or use the `shutdown` command")
        StartupApp.start(pack_cmdline_fn())
