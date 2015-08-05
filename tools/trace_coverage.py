#!/usr/bin/env python

import os
import sys
import trace
import imp
import time
import hotshot
import hotshot.stats

__usage__ = '''
Purpose: Print out test coverage information about a package.
Assume:  The package has `tests` directory with files `test_*.py`
         that contain functions `test_*()`.
Usage:   Run `trace_coverage.py [<package=sympycore>] [--profile]`
         <package> path must be in PYTHONPATH or sys.path.
Results: A summary is printed to stdout, for detailed reports
         see /tmp/<package>*.cover files.
'''
# Author:  Pearu Peterson <pearu.peterson@gmail.com>
# Created: Nov 7, 2007

show_profile = False
if '--profile' in sys.argv:
    sys.argv.remove('--profile')
    show_profile = True

package = None
if len(sys.argv)==2:
    package = sys.argv[1].replace('/','.')
else:
    package = 'sympycore'

toppackage = package.split('.')[0]
try:
    f,package_path,info = imp.find_module(toppackage)
except ImportError, msg:
    print >> sys.stderr,'Failed to locate %r: %s' % (package, msg)
    package = None

if package is None:
    print __usage__
    sys.exit()

print 'Found package %r in %r.' % (package, package_path)

package_path = os.path.dirname(package_path)
sys.path.insert(0,package_path)

p = os.path.join(package_path,package.replace('.','/')+'.py')
if os.path.isfile(p):
    parentpackage = '.'.join(package.split('.')[:-1]) or package
else:
    parentpackage = package

hotshot_target = '%s_stones.prof' % (parentpackage)
profile_target = '%s_profile.out' % (parentpackage)

def get_test_functions():
    global package, package_path
    i = 0
    test_functions = []
    for root, dirs, files in os.walk(package_path):
        if '.svn' in dirs:
            dirs.remove('.svn')
        if os.path.basename(root) not in ['tests','bench']:
            continue
        pname = root[len(package_path)+1:-6].replace('/','.')
        if not pname.startswith(parentpackage):
            if os.path.basename(root)=='bench' and package=='sympycore':
                pname = 'bench'
            else:
                continue
        for fn in files:
            if not (fn.startswith('test_') and fn.endswith('.py')):
                continue
            sys.path.insert(0, root)
            f,p,info = imp.find_module(fn[:-3])
            del sys.path[0]
            i += 1
            m = imp.load_module('%s_%s' % (fn[:-3], i), f, p, info)
            for n in dir(m):
                if not n.startswith('test_'):
                    continue
                fnc = getattr(m, n)
                if not callable(fnc) or fnc.__name__!=n:
                    continue
                fnc.test_info = '%s:%s.%s' % (pname,fn[:-3],n)
                test_functions.append(fnc)
    return test_functions

def run_test_functions(funcs):
    start = time.time()
    i = 0
    f = 0
    n = len(funcs)
    for func in funcs:
        i += 1
        print 'Executing %s (%s/%s)...' % (func.test_info,i,n),
        try:
            func()
            print 'ok'
        except Exception, msg:
            print 'FAILURE: %s' % (msg)
            f += 1
    end = time.time()
    print 'Run %s test functions in %0.5f secs.' % (len(funcs),end-start)
    if f:
        print '%s TESTS FAILED' % (f)

class MyCoverageResults(trace.CoverageResults):

    def show_results(self, coverdir='/tmp', show_missing=True):
        per_file = {}
        for filename, lineno in self.counts.keys():
            lines_hit = per_file[filename] = per_file.get(filename, {})
            lines_hit[lineno] = self.counts[(filename, lineno)]
        # accumulate summary info, if needed
        sums = {}
        for filename, count in per_file.iteritems():
            # skip some "files" we don't care about...
            if filename == "<string>":
                continue
            if filename.endswith((".pyc", ".pyo")):
                filename = filename[:-1]
            if filename.startswith('None'):
                continue
            if coverdir is None:
                dir = os.path.dirname(os.path.abspath(filename))
                modulename = modname(filename)
            else:
                dir = coverdir
                if not os.path.exists(dir):
                    os.makedirs(dir)
                modulename = trace.fullmodname(filename)
            # If desired, get a list of the line numbers which represent
            # executable content (returned as a dict for better lookup speed)
            if show_missing:
                lnotab = trace.find_executable_linenos(filename)
            else:
                lnotab = {}
            source = trace.linecache.getlines(filename)
            coverpath = os.path.join(dir, modulename + ".cover")
            n_hits, n_lines = self.write_results_file(coverpath, source,
                                                      lnotab, count)
            if n_lines:
                percent = int(100 * n_hits / n_lines)
                sums[modulename] = n_lines, percent, modulename, filename

        total_lines = 0
        total_percent_lines = 0
        rlst = {}
        nlst = {}
        for m in sums.keys():
            n_lines, percent, modulename, filename = sums[m]
            if not modulename.startswith(package) or '.tests.' in modulename:
                continue
            total_lines += n_lines
            total_percent_lines += percent * n_lines
            s = modulename.split('.')
            for i in range(len(s)):
                n = '.'.join(s[:i+1])
                if not n.startswith(package):
                    continue
                if not rlst.has_key(n):
                    rlst[n] = 0
                    nlst[n] = 0
                rlst[n] += percent * n_lines
                nlst[n] += n_lines
        if not total_lines:
            print 'Nothing to report.'
            print '-'*42
            return
        def my_cmp(lhs, rhs):
            p1, p2 = rlst[lhs]/nlst[lhs], rlst[rhs]/nlst[rhs]
            c = cmp(p1, p2)
            if not c:
                c = -cmp(nlst[lhs], nlst[rhs])
            return c
        mods = rlst.keys()
        mods.sort(my_cmp)
        i = 0
        print "-"*42
        print "lines   cov%   module"
        print "-"*42
        for m in mods:
            r = rlst[m]
            n = nlst[m]
            p = r/n
            if p<100:
                print "%5d   %3d%%   %s" % (n, p, m)
            else:
                i += 1
        total_percent = total_percent_lines/total_lines
        if i:
            print "Modules with 100% test coverage (not shown):",i
        print '-'*42
        print 'TOTAL NOF LINES: %s, TOTAL COVERAGE: %s%%' % (total_lines, total_percent)
        print '-'*42
        print 'See %s/%s*.cover files for detailed coverage reports.' % (coverdir, package)
        return

class MyTrace(trace.Trace):

    def globaltrace_lt(self, frame, why, arg):
        """Handler for call events.

        If the code block being entered is to be ignored, returns `None',
        else returns self.localtrace.
        """
        if why == 'call':
            code = frame.f_code
            filename = frame.f_globals.get('__file__', None)
            if filename:
                modulename = frame.f_globals.get('__name__', None)
                if modulename is None:
                    # XXX modname() doesn't work right for packages, so
                    # the ignore support won't work right for packages
                    modulename = trace.modname(filename)
                if modulename is not None:
                    ignore_it = self.ignore.names(filename, modulename)
                    if not ignore_it:
                        if self.trace:
                            print (" --- modulename: %s, funcname: %s"
                                   % (modulename, code.co_name))
                        return self.localtrace
            else:
                return None

    def results(self):
        return MyCoverageResults(self.counts, infile=self.infile,
                               outfile=self.outfile,
                               calledfuncs=self._calledfuncs,
                               callers=self._callers)


def trace_test_functions():
    tracer = MyTrace(ignoredirs=[sys.prefix, sys.exec_prefix,],
                         trace=0,
                         count=1)
    tracer.run('main()')
    r = tracer.results()
    r.show_results()

def profile_test_functions():
    prof = hotshot.Profile(hotshot_target)
    prof.runcall(main)
    prof.close()
    # this is used by epydoc:
    hotshot.stats.load(hotshot_target).dump_stats(profile_target)

def func_strip_path(func_name):
    filename, line, name = func_name
    while package in filename[1:]:
        i = filename[1:].index(package)+1
        filename = filename[i:]
    return filename, line, name

def strip_dirs(self):
    from pstats import func_std_string, add_func_stats
    oldstats = self.stats
    self.stats = newstats = {}
    max_name_len = 0
    for func, (cc, nc, tt, ct, callers) in oldstats.iteritems():
        newfunc = func_strip_path(func)
        if len(func_std_string(newfunc)) > max_name_len:
            max_name_len = len(func_std_string(newfunc))
        newcallers = {}
        for func2, caller in callers.iteritems():
            newcallers[func_strip_path(func2)] = caller

        if newfunc in newstats:
            newstats[newfunc] = add_func_stats(
                newstats[newfunc],
                (cc, nc, tt, ct, newcallers))
        else:
            newstats[newfunc] = (cc, nc, tt, ct, newcallers)
    old_top = self.top_level
    self.top_level = new_top = {}
    for func in old_top:
        new_top[func_strip_path(func)] = None

    self.max_name_len = max_name_len
    
    self.fcn_list = None
    self.all_callees = None
    return self

def show_profile_test_functions():
    profile_test_functions()
    stats = hotshot.stats.load(hotshot_target)
    strip_dirs(stats)
    stats.sort_stats('time','calls','time')
    stats.print_stats(40)

def main():
    run_test_functions(get_test_functions())

if __name__ == '__main__':
    if show_profile:
        show_profile_test_functions()
    else:
        trace_test_functions()

    #main()
    
