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
#force_start_revision = 2394
start_revision = 4
pkl_filename = 'cache_v1.pickle'
checkout_command1 = 'svn co http://sympy.googlecode.com/svn/trunk/sym@%s sym'
checkout_command2 = 'svn co http://sympy.googlecode.com/svn/trunk/sympy@%s sympy'
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

if start_revision<=209:
    SVN_VERSION = get_svn_revision(os.path.join(os.path.dirname(__file__),'sym'))
    if SVN_VERSION is None:
        cmd = checkout_command1 % (start_revision)
        print 'Checking out sources using:', cmd
        sts = os.system(cmd)
        if sts:
            sys.exit(sts)
    SVN_VERSION = get_svn_revision(os.path.join(os.path.dirname(__file__),'sym'))
else:
    SVN_VERSION = get_svn_revision(os.path.join(os.path.dirname(__file__),'sympy'))
    if SVN_VERSION is None:
        cmd = checkout_command2 % (start_revision)
        print 'Checking out sources using:', cmd
        sts = os.system(cmd)
        if sts:
            sys.exit(sts)
    SVN_VERSION = get_svn_revision(os.path.join(os.path.dirname(__file__),'sympy'))

def get_cache():
    if not os.path.isfile(pkl_filename) and os.path.isfile(pkl_filename+'.gz'):
        sts = os.system('gunzip %s.gz' % (pkl_filename))
        if sts:
            sys.exit(sts)
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

def timer(stmt, setup='pass',n=3000, key=None):
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
    print 'SVN_VERSION=',SVN_VERSION
    if SVN_VERSION<4:
        print 'No code in SVN version %s' % (SVN_VERSION)
        return
    elif SVN_VERSION<=13:
        setup = '''
from sym import symbol
from sym.numbers import rational
x,y,z = map(symbol,'xyz')
a,b,c = rational(1,2), rational(2,3), rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.eval:",stmt.eval()
print "stmt.expand:",stmt.expand()
'''
        stmt = '''(3*(a*x + b*y + c*z)).expand()'''
    elif 14<=SVN_VERSION<=17:
        print 'Buggy SVN version %s (inconsistent eval/expand), skipping.' % (SVN_VERSION)
        return
    elif SVN_VERSION<=156:
        setup = '''
from sym import symbol
from sym.numbers import rational
x,y,z = map(symbol,'xyz')
a,b,c = rational(1,2), rational(2,3), rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.eval:",stmt.eval()
print "stmt.expand:",stmt.expand()
if stmt.expand()==stmt.eval():
    print "STOP ME and fix stmt: change expand to eval!!!"
    sys.exit(2)
if stmt is 3*(a*x + b*y + c*z):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''(3*(a*x + b*y + c*z)).expand()'''
    elif SVN_VERSION in [157,200,317,318,319,326,519,892] or \
             1530<=SVN_VERSION<=1540 or 1614<=SVN_VERSION<=1618:
        print 'Buggy SVN version %s, skipping.' % (SVN_VERSION)
        return
    elif SVN_VERSION<=209:
        setup = '''
from sym import symbol, rational
from sym import rational
x,y,z = map(symbol,'xyz')
a,b,c = rational(1,2), rational(2,3), rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.eval:",stmt.eval()
print "stmt.expand:",stmt.expand()
if stmt.eval()==stmt.expand():
    print "STOP ME and fix stmt: change expand to eval method!!!"
    sys.exit(2)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''(3*(a*x + b*y + c*z)).expand()'''
    elif SVN_VERSION<=325:
        setup = '''
from sym import Symbol, Rational
x,y,z = map(Symbol,'xyz')
a,b,c = Rational(1,2), Rational(2,3), Rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.eval:",stmt.eval()
print "stmt.expand:",stmt.expand()
if stmt.eval()==stmt.expand():
    print "STOP ME and fix stmt: change expand to eval!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''(3*(a*x + b*y + c*z)).expand()'''
    elif SVN_VERSION<=1320 or 1425<=SVN_VERSION<=1539:
        setup = '''
from sympy import Symbol, Rational
x,y,z = map(Symbol,'xyz')
a,b,c = Rational(1,2), Rational(2,3), Rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.eval:",stmt.eval()
print "stmt.expand:",stmt.expand()
if stmt.eval()==stmt.expand():
    print "STOP ME and fix stmt: change expand to eval!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''(3*(a*x + b*y + c*z)).expand()'''
    elif SVN_VERSION<=2562:
        setup = '''
from sympy import Symbol, Rational
x,y,z = map(Symbol,'xyz')
a,b,c = Rational(1,2), Rational(2,3), Rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
if hasattr(stmt,"eval"):
    print "stmt.eval:",stmt.eval()
print "stmt.expand:",stmt.expand()
if stmt!=stmt.expand():
    print "STOP ME and fix stmt: add eval or expand!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''3*(a*x + b*y + c*z)'''
    else:
        print 'Development has been moved to HG starting 2563. Skipping this SVN version %s' % (SVN_VERSION)
        return
    key = get_cache_key((stmt, setup))
    if key is None:
        timer(stmt, setup, key=key)
    else:
        c = get_cache()[SVN_VERSION][key]
        print "(%r statements)/second [from cache]: %s" % (stmt, c)

def show():
    cache = get_cache()
    for k,v in cache.items():
        print k,max(v.values())
    
if __name__=='__main__':
    cache = get_cache()
    if force_start_revision is not None:
        start = force_start_revision -1
    elif cache:
        start = max(cache.keys())
    else:
        start = start_revision - 1
    buggy_revisions = range(1530,1541)+range(1614,1620)
    for r in range(start+1,start+500):
        if r in buggy_revisions:
            print 'Skipping this SVN version %s as it has bugs/no changes' % (r)
            continue
        if r <= 209:
            sts, output = commands.getstatusoutput(checkout_command1 % (r))
        else:
            sts, output = commands.getstatusoutput(checkout_command2 % (r))
        print output
        if sts:
            sys.exit(sts)
        if '.py' not in output and r > start+1:
            print 'Skipping this SVN version %s as no python file was changed' % (r)
            continue
        os.system('rm -f *.pyc */*.pyc */*/*.pyc */*/*/*.pyc */*/*/*/*.pyc */*/*/*/*/*.pyc')
        sts = os.system('PYTHONPATH=. python -c "from scan_svn import main; main()"')
        if sts:
            sys.exit(sts)
