#!/usr/bin/env python

# Version 2.02
# - .01 = environmental variable support
# - .02 = branch through the children of a process id

# Load Primary Libraries
import sys
# Prevents the creation of .pyc files - which appear broken on zee
sys.dont_write_bytecode = True
import os,string,time, fcntl

from subprocess import Popen, PIPE, STDOUT

##########################################
###  This is the primary run function  ###
##########################################
#http://stackoverflow.com/questions/1191374/subprocess-with-timeout
#http://thraxil.org/users/anders/posts/2008/03/13/Subprocess-Hanging-PIPE-is-your-enemy/
#http://stackoverflow.com/questions/19880190/interactive-input-output-using-python
import signal
class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

def setNonBlocking(fd):
    """
    Set the file description of the given file descriptor to non-blocking.
    """
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)

def get_process_children(pid):
    p = Popen('ps --no-headers -o pid --ppid %d' % pid, shell=True,
              stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]

def run(_exec, _input, *_envvar):
    _newenv = os.environ.copy()
    # I expect envvar to be a string like:
    # a=2
    # a=2, b=3, c=happy happy joy joy, d=4
    if _envvar:
        _envvar = string.strip(_envvar[0])
        if string.find(_envvar, ',') == -1:
            _envvar = [_envvar]
        else:
            _envvar = string.splitfields(_envvar, ',')
        for evar in _envvar:
            evar = string.strip(evar)
            if evar != '' and string.find(evar, '=') != -1:
                evar = string.splitfields(evar, '=')
                valu = string.strip(evar[1])
                evar = string.strip(evar[0])
                _newenv[evar] = valu
    _start = time.time()
    cmd = string.splitfields(string.strip(_exec), ' ')
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=_newenv)
    setNonBlocking(p.stdout)
    setNonBlocking(p.stderr)

    if _input != '':                    ###DANGER: IGNOREING writes if nothing provided!!!
        if str(type(_input)) != "<type 'list'>":
            _input = [_input]
        _input.append('\n\n\n\n')       ###DANGER: this could be bad..
        for line in _input:
            p.stdin.write(line+'\n')    ###DANGER: that \n could be bad...
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(6)                     ###HOW MUCH TIME TO GIVE THEM TO RUN THEIR PROGRAM####
    stdout = ''
    stderr = 'inf'
    try:
        #stdout, stderr = p.communicate(_input)
        stdout, stderr = p.communicate()
        signal.alarm(0)
        _return_code = p.returncode
    except Alarm:
        _return_code = 9999
        pids = [p.pid]
        try:
            stdout = stdout + p.stdout.read()
            stdout = stdout + 'Infinite loop or program did not exit'
        except Exception as e:
            #print '      SECOND FAILURE '+str(e)
            stdout = stdout + 'Infinite loop or program did not exit'
        if 1:  ## For future expandability, kill children...
            pids.extend(get_process_children(p.pid))
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    _etime = time.time() - _start
    return stdout, stderr, _return_code, _etime