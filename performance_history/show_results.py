
# Read README.txt before running this script.

import os
import re
import datetime
import cPickle as pickle
import math

use_log = True

def get_cache_1():
    pkl_filename = 'sympycore_svn/cache_v1.pickle'
    if os.path.isfile(pkl_filename):
        pkl_file = open(pkl_filename,'rb')
        cache = pickle.load(pkl_file)
        pkl_file.close()
    else:
        cache = {}
    return cache

def get_cache_2():
    pkl_filename = 'sympy_svn/cache_v1.pickle'
    if os.path.isfile(pkl_filename):
        pkl_file = open(pkl_filename,'rb')
        cache = pickle.load(pkl_file)
        pkl_file.close()
    else:
        cache = {}
    return cache

def get_cache_3():
    pkl_filename = 'sympy_research/cache_v1.pickle'
    if os.path.isfile(pkl_filename):
        pkl_file = open(pkl_filename,'rb')
        cache = pickle.load(pkl_file)
        pkl_file.close()
    else:
        cache = {}
    return cache

def get_cache_4():
    pkl_filename = 'sympy_sandbox/cache_v1.pickle'
    if os.path.isfile(pkl_filename):
        pkl_file = open(pkl_filename,'rb')
        cache = pickle.load(pkl_file)
        pkl_file.close()
    else:
        cache = {}
    return cache

def get_dates_1():
    filename = 'sympycore_svn.log'
    d = {}
    if os.path.isfile(filename):
        f = open(filename,'r')
        for line in f.readlines():
            if line.startswith('r'):
                l = line[1:].split('|')
                rev = int(l[0].strip())
                year,month,day = map(int,l[-1].split()[0].strip().split('-'))
                d[rev] = datetime.date(year, month, day)
        f.close()
    else:
        print 'Need %s. You can generate it using the following command' % (filename)
        print 'svn log -q http://sympycore.googlecode.com/svn/ > sympycore_svn.log'
        sys.exit(1)
    return d

def get_dates_2():
    filename = 'sympy_svn.log'
    d = {}
    if os.path.isfile(filename):
        f = open(filename,'r')
        for line in f.readlines():
            if line.startswith('r'):
                l = line[1:].split('|')
                rev = int(l[0].strip())
                year,month,day = map(int,l[-1].split()[0].strip().split('-'))
                d[rev] = datetime.date(year, month, day)
        f.close()
    else:
        print 'Need %s. You can generate it using the following command' % (filename)
        print 'svn log -q http://sympy.googlecode.com/svn/ > sympy_svn.log'
        sys.exit(1)
    return d

get_dates_3 = get_dates_2
get_dates_4 = get_dates_2

min_date = datetime.date(2006, 2, 1)

def get_dates_data(cache, rev_dates):
    keys = cache.keys()
    keys.sort()
    dates = []
    data = []
    for k in keys:
        if k not in rev_dates:
            continue
        v = cache[k]
        d = rev_dates[k]
        if d < min_date:
            continue
        dates.append(d)
        v = max(v.values())
        #if use_log:
        #    v = math.log10(v)
        data.append(v)
    return dates, data

from matplotlib.dates import MONDAY, SATURDAY
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from pylab import figure, show

mondays   = WeekdayLocator(MONDAY)    # every monday
months    = MonthLocator(range(1,13), bymonthday=1)           # every month
monthsFmt = DateFormatter("%b '%y")

dates1, data1 = get_dates_data(get_cache_1(), get_dates_1())
dates2, data2 = get_dates_data(get_cache_2(), get_dates_2())
dates3, data3 = get_dates_data(get_cache_3(), get_dates_3())
dates4, data4 = get_dates_data(get_cache_4(), get_dates_4())
#dates5, data5 = [datetime.date(2007, 1, 7)], [540]



fig = figure()
ax = fig.add_subplot(111)
ax.plot_date(dates2, data2, 'o')
ax.plot_date(dates3, data3, 'o')
ax.plot_date(dates4, data4, 'o')
ax.plot_date(dates1, data1, 'o')
ax.plot_date([datetime.date(2008, 7, 1)], [180000], 'o')
ax.plot_date([datetime.date(2008, 7, 1)], [110000], 'o')
ax.plot_date([datetime.date(2008, 7, 1)], [19400], 'o')
ax.plot_date([datetime.date(2008, 7, 1)], [15700], 'o')
ax.plot_date([datetime.date(2008, 7, 1)], [13400], 'o')
ax.plot_date([datetime.date(2008, 7, 1)], [2320], 'o')
ax.plot_date([datetime.date(2008, 7, 1)], [780], 'o')
ax.plot_date([datetime.date(2008, 7, 1)], [540], 'o')

ax.plot_date([datetime.date(2008, 7, 1)], [35], 'o')
if use_log:
    ax.set_yscale('log')
ax.legend((
           'SymPy SVN',
           'sympy-research branch',
           'sympy-sandbox branch',
           'Sympy Core SVN: 33 800 execs/sec',
           'GiNaC: 180 000 exec/sec',
           'Sage(libSingular): 110 000 exec/sec',
           #'Singular(3.0.4): 58 000 exec/sec', # singular prompt has overhead
           'Maxima(GCL): 19 400 exec/sec',
           'pyginac: 15 700 execs/sec',
           'swiginac: 13 400 execs/sec',
           'Maxima(clisp): 2 320 exec/sec',
           'SymPy, Mercurial: 780 execs/sec',
           'symbolic: 540 execs/sec',
           'Sage(Maxima): 35 exec/sec',
           ), loc=2)
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(monthsFmt)
ax.xaxis.set_minor_locator(mondays)
ax.title.set_text('''Performance history of Python based CAS-s
Executing: 3*(1/2*x + 2/3*y + 4/5*z) -> 3/2*x + 2*y + 12/5*z''')
ax.xaxis.label.set_text('Time')
ax.yaxis.label.set_text('Number of executions per second')
ax.autoscale_view()
#ax.xaxis.grid(False, 'major')
#ax.xaxis.grid(True, 'minor')
ax.grid(True)

fig.autofmt_xdate()

#fig.savefig('results')
show()
