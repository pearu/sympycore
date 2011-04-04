
import sympycore

def obj2num(s, abs_tol=1e-16):
    if isinstance(s, str):
        f = eval(s)
    else:
        f = s
    #return float(f) # will induce numerical errors and incorrect rank for GJE algorithm.
    i = int (f)
    if i==f:
        return i
    return sympycore.f2q(f, abs_tol)

def time2str(s, last_unit='s'):
    """ Return human readable time string from seconds.

    Examples
    --------
    >>> from iocbio.utils import time_to_str
    >>> print time_to_str(123000000)
    3Y10M24d10h40m
    >>> print time_to_str(1230000)
    14d5h40m
    >>> print time_to_str(1230)
    20m30.0s
    >>> print time_to_str(0.123)
    123ms
    >>> print time_to_str(0.000123)
    123us
    >>> print time_to_str(0.000000123)
    123ns

    """
    seconds_in_year = 31556925.9747 # a standard SI year
    orig_s = s
    years = int(s / (seconds_in_year))
    r = []
    if years:
        r.append ('%sY' % (years))
        s -= years * (seconds_in_year)
    if last_unit=='Y': s = 0
    months = int(s / (seconds_in_year/12.0))
    if months:
        r.append ('%sM' % (months))
        s -= months * (seconds_in_year/12.0)
    if last_unit=='M': s = 0
    days = int(s / (60*60*24))
    if days:
        r.append ('%sd' % (days))
        s -= days * 60*60*24
    if last_unit=='d': s = 0
    hours = int(s / (60*60))
    if hours:
        r.append ('%sh' % (hours))
        s -= hours * 60*60
    if last_unit=='h': s = 0
    minutes = int(s / 60)
    if minutes:
        r.append ('%sm' % (minutes))
        s -= minutes * 60
    if last_unit=='m': s = 0
    seconds = int(s)
    if seconds:
        r.append ('%ss' % (seconds))
        s -= seconds
    if last_unit=='s': s = 0
    mseconds = int(s*1000)
    if mseconds:    
        r.append ('%sms' % (mseconds))
        s -= mseconds / 1000    
    if last_unit=='ms': s = 0
    useconds = int(s*1000000)
    if useconds:
        r.append ('%sus' % (useconds))
        s -= useconds / 1000000
    if last_unit=='us': s = 0
    nseconds = int(s*1000000000)
    if nseconds:
        r.append ('%sns' % (nseconds))
        s -= nseconds / 1000000000
    if not r:
        return '0'
    return ''.join(r)
