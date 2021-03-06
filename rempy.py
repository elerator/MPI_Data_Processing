import pexpect
import sys
import time
import re


class RemotePython:
    def __init__(self, commands = "", server = "", lib_path = "", stream = None, libpath = None):
        self.commands = commands#List of commands to be executed remotely
        self.server = server
        self.python_running = False
        if(libpath == None):
            print("Using default libpath")
            self.libpath = "python_scripts.MPI_Data_Processing.mot"
            print("libpath: " + self.libpath)

        if(stream == None):
            if(server == ""):
                self.server = pexpect.spawnu("getserver -sL", logfile = sys.stdout, echo = False)
            else:
                self.server = pexpect.spawnu("ssh " + server, logfile = sys.stdout, echo = False)
        else:
            if(server == ""):
                self.server = pexpect.spawnu("getserver -sL", logfile = stream, echo = False)
            else:
                self.server = pexpect.spawnu("ssh " + server, logfile = stream, echo = False)

        time.sleep(2)
        self.server.expect(".")
        self.server.expect(".*")

        self.start_python()

    def start_python(self):
        if(self.python_running):
            print("-- restarting python")
            self.server.sendline("quit()")
        self.server.sendline("python3.5")
        self.server.expect(">>>")
        self.fast_command("from " + self.libpath + " import *")

    @staticmethod
    def assemble_command(string,replacements):
        res = ""
        cur_pos = 0
        pos = [(m.start(0), m.end(0)) for m in re.finditer("{}", string)]
        for x, replace in zip(pos, replacements):
            res += string[cur_pos:x[0]]
            res += replace
            cur_pos = x[1]
        res += string[cur_pos:len(string)]
        return res

    def fast_command(self, command):
        self.server.sendline(command)
        self.server.expect(">>>", timeout= 10)
        #try:
        #    self.server.after()
        #except:
        #    pass


    def long_command(self, command, expectation = "\n", repetitive = True, timeout = 10):
        if(type(command)==type([]) and type(expectation) == type([])):
            for c, e in zip(command,expectation):
                self.long_command(c, expectation)
        else:#Assuming strings
            self.server.sendline(command)
            while(True):
                try:
                    self.server.expect(expectation, timeout = timeout)
                except Exception as e:
                    try:
                        self.server.expect(">>>", timeout = timeout)
                        break
                    except:
                        pass


    def abort_command(self):
        self.server.send('\003')
