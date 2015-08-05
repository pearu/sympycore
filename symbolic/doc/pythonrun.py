#/usr/bin/env python
#
# Python Daemon for pythonrun.sty
#
# Author: Pearu Peterson <pearu.peterson@gmail.com>
# Created: March 2007
#

__usage__ = '''
pythonrun [<options>] <start|stop|exec|eval|distil>

start - start python daemon
stop  - stop python daemon
exec  - use python daemon to execute python commands read from stdin
eval  - use python daemon to evaluate python expression read from stdin
distil - distil latex source, options: source=<filename>, target=<filename>
'''
from cStringIO import StringIO
import os
import re
import sys
import signal
import Pyro.core
import traceback
import atexit
import textwrap
import subprocess
import time

PORT=7769
HOST='localhost'
LINEWIDTH = 60
def wrap(line, width=LINEWIDTH):
    return '\\\n'.join(textwrap.wrap(line,width))

lock_file = '.pythonrun.lock'

def set_lock():
    pid = os.getpid()
    f = open(lock_file,'w')
    f.write(str(pid))
    f.close()
    return pid
def get_lock():
    f = open(lock_file,'r')
    pid = f.read().strip()
    f.close()
    return int(pid)
def remove_lock(lock_file=lock_file):
    if os.path.isfile(lock_file):
        os.remove(lock_file)
    return

class PythonSession(Pyro.core.ObjBase):

    def __init__(self, daemon = None):
        Pyro.core.ObjBase.__init__(self)
        self.daemon = daemon
        self.locals = {}
        self.globals = {'__name__':'__daemon__',
                        '__file__':__file__,
                        '__builtins__':__builtins__}
        return

    def execute(self, code, **params):
        io = StringIO()
        stdout = sys.stdout
        stderr = sys.stderr
        sys.stdout = sys.stderr = io
        result = None
        try:
            print eval(code, self.globals, self.locals)
        except SyntaxError:
            exec code in self.globals, self.locals
        except Exception:
            traceback.print_exc(file=io)
        textwidth = params.get('textwidth',300)
        em = params.get('em',10)
        pt2char = 1.95/em
        output = wrap(io.getvalue().rstrip(),int(textwidth*pt2char))
        sys.stdout = stdout
        sys.stderr = stderr
        return output

    def evaluate(self, code, **params):
        try:
            return str(eval(code, self.globals, self.locals))
        except Exception:
            traceback.print_exc()
        return code

def start_daemon():
    stop_daemon()

    Pyro.core.initServer(banner=0)
    daemon=Pyro.core.Daemon(host=HOST,port=PORT)
    uri=daemon.connect(PythonSession(daemon), "pythonrun")

    pid = set_lock()
    atexit.register(remove_lock)

    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        pass
    daemon.shutdown()
    return

def stop_daemon():
    if os.path.isfile(lock_file):
        pid = get_lock()
        if pid:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
            remove_lock()
    return

def process_stdin(**params):
    Pyro.core.initClient(banner=0)
    session = Pyro.core.getProxyForURI("PYROLOC://%s:%s/pythonrun" % (HOST, PORT))
    lines = sys.stdin.readlines()
    code_lines = []
    while lines or code_lines:
        if not code_lines and lines:
            code_lines.append(lines.pop(0))
        elif lines and lines[0][:1].isspace():
            code_lines.append(lines.pop(0))
        else:
            code = (''.join(code_lines)).rstrip()
            display_code = ('>>> ' + '... '.join(code_lines)).rstrip()
            print display_code
            result = session.execute(code,**params)
            if result:
                print result
            code_lines = []
    return

def process_eval_stdin(**params):
    Pyro.core.initClient(banner=0)
    session = Pyro.core.getProxyForURI("PYROLOC://%s:%s/pythonrun" % (HOST,PORT))
    print session.evaluate(sys.stdin.read().strip(),**params)
    return

def process_parameters():
    params = {}
    for a in sys.argv:
        if '=' in a:
            n,v = a.split('=',1)
            if v.endswith('pt'):
                v = float(v[:-2])
            params[n] = v
    return params

def distil_latex(**params):
    source = params.get('source',None)
    if not source or not os.path.isfile(source):
        print >> sys.stderr, 'Non-existing source:',source
        return
    target = params.get('target', os.path.join(os.path.dirname(source),
                                               'distil_%s' % (os.path.basename(source))))
    print 'Starting python daemon in background'
    subprocess.Popen([sys.executable+" pythonrun.py start"],shell=True)
    time.sleep(0.3)
    f = open(source,'r')
    source_block = f.read()
    f.close()
    match_python_block = re.compile(r'^\s*\\begin\s*\{(?P<kind>python(latex|\s*[*]?))\s*\}(?P<block>.*?)^\s*\\end\s*\{python(latex|\s*[*]?)\s*\}',
                                    re.M | re.S)
    match_python_eval = re.compile(r'^[^%\n]*\\pythoneval\s*\{(?P<block>.*?)\}',re.M | re.S)

    target_block = ''
    
    while source_block:
        m1 = match_python_block.search(source_block)
        m2 = match_python_eval.search(source_block)
        if m1 and m2:
            if m1.start() < m2.start(): m = m1; func = replace_python_block
            else: m = m2; func = replace_python_eval
        elif m1: m = m1; func = replace_python_block
        elif m2: m = m2; func = replace_python_eval
        else:
            target_block += source_block
            break
        target_block += source_block[:m.start()]
        target_block += func(m, source_block[m.start():m.end()])
        source_block = source_block[m.end():]

    print 'Stopping python daemon'
    subprocess.Popen([sys.executable+" pythonrun.py stop"],shell=True)

    target_block = target_block.replace(r'\usepackage{pythonrun}','').replace(r'\pythonstopdaemon','')

    f = open(target, 'w')
    f.write(target_block)
    f.close()
    return

def replace_python_eval(m, source):
    content = m.group('block').strip()
    p = subprocess.Popen(["%s pythonrun.py eval" % (sys.executable)],
                         shell=True, stdin=subprocess.PIPE,bufsize=-1,
                         stdout=subprocess.PIPE, close_fds=True)
    p.stdin.write(content)
    p.stdin.close()
    output = p.stdout.read().strip()
    return source[:source.find(r'\pythoneval')] + output

def replace_python_block(m, source):
    content = m.group('block').strip()
    kind = m.group('kind')
    if kind.endswith('latex'):
        cmd = "%s pythonrun.py eval" % (sys.executable)
    else:
        cmd = "%s pythonrun.py textwidth=420pt exec" % (sys.executable)
    p = subprocess.Popen([cmd],
                         shell=True, stdin=subprocess.PIPE,bufsize=-1,
                         stdout=subprocess.PIPE, close_fds=True)
    p.stdin.write(content)
    p.stdin.close()
    output = p.stdout.read().strip()
    if kind.endswith('*'): return ''
    if kind.endswith('latex'):
        return output
    return '''\\begin{verbatim}
%s
\\end{verbatim}''' % (output)

if __name__=="__main__":

    if sys.argv[-1]=='start':
        start_daemon()
    elif sys.argv[-1]=='stop':
        stop_daemon()
    elif sys.argv[-1]=='exec':
        process_stdin(**process_parameters())
    elif sys.argv[-1]=='eval':
        process_eval_stdin(**process_parameters())
    elif sys.argv[-1]=='distil':
        distil_latex(**process_parameters())
    else:
        print sys.argv
        print __usage__
