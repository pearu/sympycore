#
# Checkout working revisions of sympy from SVN repository,
# run timing tests, and save results to file.
#
# Author: Pearu Peterson
# Created: December 2007
#
# NOTES: This program is developed under Debian system, running it
# under other systems one may need to modify it.  This program is
# semi-automatic and one may need to modify svn tree in order to check
# out new revisions and run tests (one needs to disable caching).
#
# To run tests from scratch, move away the file specified in pkl_filename.
#
# To disable caching, return func in cache_it* functions and
# Memoizer.__call__ method.

import os
import re
import sys
import timeit
import commands
import cPickle as pickle
from numpy.distutils.misc_util import njoin

force_start_revision = None
#force_start_revision = 1446
start_revision = 1150
pkl_filename = 'cache_v1.pickle'
checkout_command = 'svn co http://sympy.googlecode.com/svn/branches/sympy-research/sympy@%s sympy'
sys.path.insert(0, os.path.dirname(__file__))


def get_svn_revision(path):
    """Return path's SVN revision number.
    """
    # copied from  numpy/distutils/misc_util.py
    revision = None
    m = None
    try:
        sin, sout = os.popen4('svnversion')
        m = re.match(r'(?P<revision>\d+)', sout.read())
    except:
        pass
    if m:
        revision = int(m.group('revision'))
        return revision
    if sys.platform=='win32' and os.environ.get('SVN_ASP_DOT_NET_HACK',None):
        entries = njoin(path,'_svn','entries')
    else:
        entries = njoin(path,'.svn','entries')
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
    return revision

if force_start_revision is not None:
    start_revision = force_start_revision

SVN_VERSION = get_svn_revision(os.path.join(os.path.dirname(__file__),'sympy'))
if SVN_VERSION is None:
    cmd = checkout_command % (start_revision)
    print 'Checking out sources using:', cmd
    sts = os.system(cmd)
    if sts:
        sys.exit(sts)
SVN_VERSION = get_svn_revision(os.path.join(os.path.dirname(__file__),'sympy'))

def get_cache():
    if os.path.isfile(pkl_filename):
        pkl_file = open(pkl_filename,'rb')
        cache = pickle.load(pkl_file)
        pkl_file.close()
    else:
        cache = {}
    return cache

def dump_cache(cache):
    pkl_file = open(pkl_filename,'wb')
    pickle.dump(cache, pkl_file)
    pkl_file.close()

def get_cache_key(key):
    cache = get_cache()
    d = cache.get(SVN_VERSION)
    if d is not None:
        for k, v in d.items():
            if k[0]==key[0]:
                return k
    return None

def timer(stmt, setup='pass',n=5000,key=None):
    cache = get_cache()
    if key is None:
        key = (stmt, setup)
        key = get_cache_key(key)
    if key is None:
        key = (stmt, setup)
        t = timeit.Timer(stmt=stmt, setup=setup)
        try:
            c = int(n/min(t.repeat(repeat=3, number=n)))
            print "(%r statements)/second: %s" % (stmt,c)
            # (<statement>, <setup code>): <how many statements can be executed in 1 sec>)
            cache[SVN_VERSION] = {key: c}
            dump_cache(cache)
        except:
            t.print_exc()
            sys.exit(1)

def main():
    global SVN_VERSION
    print 'SVN_VERSION=',SVN_VERSION
    if SVN_VERSION<1150:
        print 'No working code in SVN version %s' % (SVN_VERSION)
        return
    elif SVN_VERSION in []:
        print 'Buggy SVN version %s, skipping.' % (SVN_VERSION)
        return
    elif SVN_VERSION<1158:
        setup = '''
from sympy import Symbol, Rational
x,y,z = map(Symbol,'xyz')
a,b,c = Rational(1,2), Rational(2,3), Rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
if hasattr(stmt, "eval"):
    print "stmt.eval:",stmt.eval()
if hasattr(stmt, "expand"):
    print "stmt.expand:",stmt.expand()
if stmt==stmt.expand():
    print "STOP ME and fix stmt: rm expand!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''(3*(a*x + b*y + c*z)).expand()'''
    elif SVN_VERSION<=2100:
        setup = '''
from sympy import Symbol, Rational
x,y,z = map(Symbol,'xyz')
a,b,c = Rational(1,2), Rational(2,3), Rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.expand:",stmt.expand()
if stmt!=stmt.expand():
    print "STOP ME and fix stmt: add expand!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''3*(a*x + b*y + c*z)'''
    else:
        print 'No test specified for given revision'
        return
    key = get_cache_key((stmt, setup))
    if key is None:
        timer(stmt, setup, key=key)
    else:
        c = get_cache()[SVN_VERSION][key]
        print "(%r statements)/second [from cache]: %s" % (stmt, c)


if __name__=='__main__':
    cache = get_cache()
    if force_start_revision is not None:
        start = force_start_revision -1
    elif cache:
        start = max(cache.keys())
    else:
        start = start_revision - 1
    skip_revisions = [1398,1399] + range(1182,1310) + range(1330,1347)
    for r in range(start+1,start+200):
        if r in skip_revisions:
            print 'Skipping this SVN version %s that is buggy or has no changes' % (r)
            continue
        sts, output = commands.getstatusoutput(checkout_command % (r))
        print output
        if sts:
            sys.exit(sts)
        if '.py' not in output and r>start+1:
            print 'Skipping this SVN version %s as no python file was changed' % (r)
            continue
        os.system('rm -f *.pyc */*.pyc */*/*.pyc */*/*/*.pyc */*/*/*/*.pyc */*/*/*/*/*.pyc')
        sts = os.system('PYTHONPATH="." python -c "from scan_svn import main; main()"')
        if sts:
            sys.exit(sts)
