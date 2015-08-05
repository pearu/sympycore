#
# Author: Pearu Peterson
# Created: February 2008
#

import re
import os
import sys
import glob
import platform
import subprocess
import shutil
from StringIO import StringIO
import tempfile

def get_platform():
    platform_info = platform.platform(1,1).replace('-generic-','-')
    if '-with-' in platform_info:
        platform_info = platform_info[:platform_info.index('-with-')]
    platform_info += '-py%s' % (platform.python_version())
    return platform_info

svn_exec = 'svn'
svnversion_exec = 'svnversion'

current_dir = os.path.abspath(os.path.dirname(__file__))

checkout_target = os.path.join(current_dir,'cache','svn_sympycore%(revision)s')
checkout_cmd = 'co http://sympycore.googlecode.com/svn/trunk@%(revision)s '
results_dir = os.path.join(current_dir, 'results', get_platform(), '%(revision)s')

def runcommand(cmd, cwd='.', verbose=2, **env):
    old_env = os.environ.copy()
    old_env.update(env)
    env = old_env
    if isinstance(cmd, list):
        cmd_str = ' '.join(cmd)
    else:
        cmd_str = str(cmd)
    if verbose:
        print 'Running %r in %r' % (cmd_str, cwd)
    fn = tempfile.mktemp()
    f = open(fn,'w')
    sts = subprocess.call(cmd, env=env, cwd=cwd, stdout=f)
    f.close()
    f = open(fn,'r')
    output = f.read()
    f.close()
    os.remove(fn)
    if verbose>1:
        print output
    if sts and verbose:
        print 'Command %r failed with status %s' % (cmd, sts)
    return sts, output

head_target = checkout_target % dict(revision='HEAD')

if not os.path.isdir(head_target):
    sts, output = runcommand([svn_exec]+ ((checkout_cmd + checkout_target) %\
                                   dict(revision='HEAD')).split(), verbose=1)
    if sts:
        sys.exit(sts)
else:
    sts, output = runcommand([svn_exec,'update'], cwd=head_target,
                             verbose = 1)

bench_dir = os.path.join(head_target, 'bench')
test_files = glob.glob(os.path.join(bench_dir,'test_*.py'))

sts, output = runcommand(svnversion_exec, cwd=head_target)
if sts:
    revision = None
    path = head_target
    if sys.platform=='win32' and os.environ.get('SVN_ASP_DOT_NET_HACK',None):
        entries = os.path.join(path,'_svn','entries')
    else:
        entries = os.path.join(path,'.svn','entries')
    if os.path.isfile(entries):
        f = open(entries)
        fstr = f.read()
        f.close()
        if fstr[:5] == '<?xml':  # pre 1.4
            m = re.search(r'revision="(?P<revision>\d+)"',fstr)
            if m:
                revision = int(m.group('revision'))
        else:  # non-xml entries file --- check to be sure that
            m = re.search(r'dir[\n\r]+(?P<revision>\d+)', fstr)
            if m:
                revision = int(m.group('revision'))
    if revision is None:
        print 'Failed to determine svn version of',path
        sys.exit()
    head_revision = revision
else:
    head_revision = int(output)

def get_stones(output):
    for line in output.splitlines():
        if line.startswith('TIMER_STONES'):
            return eval(line.split('=')[-1].strip(),{},{})
    return
def get_title(output):
    for line in output.splitlines():
        if line.startswith('TIMER_TITLE'):
            return eval(line.split('=',1)[1].strip(),{},{})
    return

for i in range(0,500,1):
    revision = head_revision - i
    if revision < 243:
        # package sympycore was introduced in revision 243
        break
    print 'REVISION=', revision
    rev_target = checkout_target % dict(revision=revision)
    if not os.path.isdir(rev_target):
        sts, output = runcommand([svn_exec]+((checkout_cmd + checkout_target) %\
                                             dict(revision=revision)).split(),
                                 verbose=1)
        if sts:
            sys.exit(sts)
    else:
        # cleanup
        dirs = []
        for n in ['doc','research','bench']:
            dirs.append(os.path.join(rev_target,n))
        for i in range(1,8):
            dirs += glob.glob(os.path.join(rev_target,*(['*']*i + ['.svn'])))
        for d in dirs:
            shutil.rmtree(d,ignore_errors=True)
        files = []
        for i in range(1,8):
            files += glob.glob(os.path.join(rev_target,*(['*']*i + ['*.pyo'])))
        map(os.remove, files)

    res_dir = results_dir % dict(revision=revision, head_revision=head_revision)
    if not os.path.isdir(res_dir):
        print 'Creating',`res_dir`,'directory'
        os.makedirs(res_dir)
    if revision > 834:
        sts, output = runcommand([sys.executable,'setup.py','build_ext','--inplace'],
                                 cwd=rev_target, verbose=1)
        if sts:
            print output
            continue
    for test_file in test_files:
        f = open(test_file,'r')
        content = f.read()
        f.close()
        rev = None
        rev_line = None
        for line in content.splitlines():
            if line.startswith('START_REVISION'):
                l = line.split('=',1)[-1].strip()
                if l:
                    rev_line = line
                    rev = int(l)
                    break
        if rev is not None and rev > revision:
            print 'Skipping',fn,'(it requires revision %s or newer)' % (rev)
            continue
        if rev_line is not None:
            h0 = hash(content)
            content = content.replace(rev_line,'')
            h = hash(content)
        else:
            h0 = h = hash(content)
        fn = os.path.join(res_dir, os.path.basename(test_file))
        if os.path.isfile(fn):
            h1 = None
            f = open(fn)
            for line in f.readlines():
                if line.startswith('HASH'):
                    h1 = int(line.split('=',1)[1].strip())
            if h1==h:
                continue
            print 'Recomputing',fn
        sts, output = runcommand([sys.executable, '-O', test_file,
                                  'REVISION=%s' %(revision)],
                                 cwd=rev_target, PYTHONPATH=rev_target)
        if sts:
            #sys.exit(sts)
            continue
        stones = get_stones(output)
        if stones is None:
            continue
        title = get_title(output)
        print 'Saving results to',fn
        f = open(fn, 'w')
        print >> f, 'TITLE=%r' % title
        print >> f, 'STONES=%s' % stones
        print >> f, 'HASH=%s' % h
        f.close()
