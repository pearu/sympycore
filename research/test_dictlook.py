
from timeit import Timer

class BaseExpr(object):

    def __init__(self, seq):
        self.seq = tuple(seq)    
        self._cache_repr = None
        self._cache_hash = None

    def __repr__(self):
        r = self._cache_repr
        if r is None or 1:
            seq = self.seq
            if isinstance(seq, tuple):
                r = '%s([%s])' % (type(self).__name__, ', '.join(map(repr,seq)))
            else:
                r = '%s(%r)' % (type(self).__name__, seq)
            self._cache_repr = r
        return r

    def __eq__(self, other):
        if type(self) is type(other):
            return self.seq == other.seq
        return False

class Expr1(BaseExpr):

    def __hash__(self):
        h = self._cache_hash
        if h is None or 1:
            self._cache_hash = h = hash(repr(self))
        return h

class Expr2(BaseExpr):

    def __hash__(self):
        h = self._cache_hash
        if h is None or 1:
            self._cache_hash = h = hash(self.seq)
        return h

l1 = [Expr1([-1])]
l2 = [Expr2([-1])]
for i in range(20):
    e = Expr1([i, l1[-1]])
    l1.append(e)
    e = Expr2([i, l2[-1]])
    l2.append(e)

e1 = Expr1(l1)
e2 = Expr2(l2)
d = dict([(e1,1), (e2,4)])

if __name__ == '__main__':
    print d.get(e1)
    timer = Timer('d.get(e1)','from test_dictlook import d, e1, e2')
    print timer.timeit(10000)
    #timer = Timer('d.get(repr(e2))','from test_dictlook import d, e1, e2')
    #print timer.timeit(10000)
    print d.get(e2)
    timer = Timer('d.get(e2)','from test_dictlook import d, e1, e2')
    print timer.timeit(10000)
    #timer = Timer('d.get(repr(e1))','from test_dictlook import d, e1, e2')
    #print timer.timeit(10000)
