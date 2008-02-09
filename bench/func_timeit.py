import math
import timeit

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

    def __init__(self, test_func):
        """
        """
        self.timer = timeit.default_timer
        src = template
        self.src = src # Save for traceback display
        code = compile(src, dummy_src_name, "exec")
        ns = dict(test_func=test_func)
        exec code in globals(), ns
        self.inner = ns["inner"]

        base_timer = timeit.Timer('foo()','def foo(): pass')
        self.base_timing = min(base_timer.repeat(repeat=3, number=100000))/100000

    def smart_timeit(self, repeat=3, verbose=True):
        units = ["s", "ms", "\xc2\xb5s", "ns"]
        scaling = [1, 1e3, 1e6, 1e9]
        precision = 3
        
        number = 1
        for i in range(1, 10):
            number *= 10
            if self.timeit(number) >= 0.2:
                break
        result = sorted(self.repeat(repeat=repeat, number=number))

        best = result[0] / number

        if best > 0.0:
            order = min(-int(math.floor(math.log10(best)) // 3), 3)
        else:
            order = 3
        if verbose:
            print "%d loops, best of %d: %.*g %s per loop" % (number, repeat,
                                                              precision,
                                                              best * scaling[order],
                                                              units[order])
        return best/self.base_timing
