#!/usr/bin/env python3

# Submit System Grader Version 3.0
# This library will handle running external programs

# Runner Version 2.10
# - .01 = environmental variable support
# - .02 = branch through the children of a process id
# - .10 = update to support python3

# Load in sys to prevent .pyc and cache files
import sys
sys.dont_write_bytecode = True

# Load Primary Libraries
import os, string, time, fcntl

# Load in Subprocess (used to run external programs)
from subprocess import Popen, PIPE, STDOUT

# Build the alarm section (to kill a program in process)
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

# This is the function that will run all external code
def run(_exec, _input, _timeout=20, _envvar={}, _shell=True):
    if not isinstance(_timeout, int):
        try:
            _timeout = int(_timeout)
        except:
            _timeout = 20
    _newenv = os.environ.copy()
    for key in _envvar:
        os.environ[key] = _envvar[key]
    _start = time.time()
    p = Popen(_exec, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=_newenv, shell=_shell)
    setNonBlocking(p.stdout)
    setNonBlocking(p.stderr)

    if _input != '' and _input is not None:
        if not isinstance(_input, list):
            _input = [_input]
        _input.append('\n\n\n\n')       ###DANGER: this could be bad..
        for line in _input:
            if not isinstance(line, bytes):
                line = bytes(line, 'utf-8')
            p.stdin.write(line)
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(_timeout)
    stdout = ''
    stderr = 'inf'
    try:
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
            stdout = stdout + 'Infinite loop or program did not exit'
        pids.extend(get_process_children(p.pid))
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    os.environ = _newenv
    _etime = time.time() - _start
    return stdout, stderr, _return_code, _etime


##########################################
###  References                        ###
##########################################
#http://stackoverflow.com/questions/1191374/subprocess-with-timeout
#http://thraxil.org/users/anders/posts/2008/03/13/Subprocess-Hanging-PIPE-is-your-enemy/
#http://stackoverflow.com/questions/19880190/interactive-input-output-using-python
