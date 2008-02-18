import sys
import math
import timeit

def run_tests(seq):
    titles = []
    stones = []
    for func in seq:
        timer = Timer(func, verbose=1)
        stone = timer.smart_timeit(verbose=1)
        titles.append(timer.title)
        stones.append(int(stone+0.5))
    print 'TIMER_TITLES=',`titles`
    print 'TIMER_STONES=',`stones`

template = """
def inner(_it, _timer, _func=test_func):
    _t0 = _timer()
    for _i in _it:
        _func()
    _t1 = _timer()
    return _t1 - _t0
"""
dummy_src_name = '<func-timeit-src>'

class Timer(timeit.Timer):

    def __init__(self, test_func, verbose=2):
        self.disable = False
        rev = None
        for l in sys.argv:
            if l.startswith('REVISION'):
                rev = int(l.split('=')[-1].strip())
                break
        if rev and hasattr(test_func, 'MIN_REVISION'):
            if rev < test_func.MIN_REVISION:
                print 'Given test function %s requires %s revision as minimum but got %s'\
                      % (test_func, test_func.MIN_REVISION, rev)
                self.disable = True
                return

        doc = getattr(test_func, '__doc__')
        if doc is None:
            doc = str(test_func)
        self.title = title = doc.lstrip().splitlines()[0].strip()
        self.timer = timeit.default_timer
        src = template
        self.src = src # Save for traceback display
        code = compile(src, dummy_src_name, "exec")
        ns = dict(test_func=test_func)
        exec code in globals(), ns
        self.inner = ns["inner"]

        number = 100000
        self.base_best = min(timeit.Timer('foo()','def foo(): pass').repeat(repeat=5, number=number))/number

    def smart_timeit(self, repeat=3, verbose=2):
        if self.disable:
            return -1
        if verbose:
            print 'Running benchmark titled %r' % (self.title)
        units = ["s", "ms", "\xc2\xb5s", "ns"]
        scaling = [1, 1e3, 1e6, 1e9]
        precision = 3
        
        number = 2
        for i in range(1, 10):
            number *= 2
            t = self.timeit(number)
            if t >= 0.1:
                break
        
        result = self.repeat(repeat=repeat, number=number)

        best = min(result) / number

        if best > 0.0:
            order = min(-int(math.floor(math.log10(best)) // 3), 3)
        else:
            order = 3
        if verbose:
            print "%d loops, best of %d: %.*g %s per loop" % (number, repeat,
                                                              precision,
                                                              best * scaling[order],
                                                              units[order])

        stones = best / self.base_best
        if verbose>1:
            print 'TIMER_TITLE=',`self.title`
            print 'TIMER_STONES=%s' % (int(stones+0.5))
        return stones
        
