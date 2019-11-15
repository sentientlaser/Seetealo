#!/usr/bin/env python3

import os

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'values.py')).read())
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shared', 'ctl.py')).read())


def start():
    serverscript = Main.relative("blender-ctl-server.py")
    argpack = StartupApp.pack(['--enable-autoexec', '--python', serverscript], Main.args())
    StartupApp.invoke(argpack)

def shutdown():
    ShutdownApp.invoke()

def signal():
    sigpack = SendSignal.pack({'rltex':'R', 'export':'E'})
    SendSignal.invoke(sigpack, Main.args)


main = Main.create({
    "startup"  : start,
    "shutdown" : shutdown,
    "signal"   : signal
})

if __name__ == "__main__":
    main()
