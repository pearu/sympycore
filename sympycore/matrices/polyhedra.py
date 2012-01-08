
from sympycore import Logic, SymbolicEquality, Calculus, heads
from . import Matrix

class Polyhedron(object):

    def __init__(self, *exprs):
        self.A = Matrix(0,1)
        self.I = []
        self.L = []
        self.names = ['*']
        for expr in exprs:
            self.add(expr)
    
    def add(self, expr):
        """ Add extra contraint to polyhedron.
        """
        if isinstance(expr, str):
            if '=' in expr or '<' in expr or '>' in expr:
                expr = Logic(expr)
            else:
                expr = Logic(expr+'==0')
        elif isinstance (expr, Calculus):
            expr = Logic (heads.EQ, (expr, Calculus(0)))
        if not isinstance(expr, Logic):
            raise NotImplementedError (`expr`) # expected Logic instance

        op, (lhs, rhs) = expr.pair
        i = self.A.rows

        if op==heads.EQ:
            expr = lhs - rhs
            self.L.append(i)
        elif op in [heads.LT, heads.LE]:
            op = heads.GE
            expr = rhs - lhs
            self.I.append(i)
        elif op in [heads.GT, heads.GE]:
            op = heads.GE
            expr = lhs - rhs
            self.I.append(i)
        else:
            raise NotImplementedError(`op`) # expected ==, <, <=, >, >=

        expr = expr.to(heads.TERM_COEFF_DICT)

        rowdict = dict()

        if expr.head is heads.NUMBER:
            self.A[i,0] = expr.data
        elif expr.head is heads.TERM_COEFF:
            term, coeff = expr.data
            try:
                j = self.names.index(term)
            except ValueError:
                j = len(self.names)
                self.names.append(term)
            self.A[i,j] = coeff
        elif expr.head is heads.TERM_COEFF_DICT:
            for term, coeff in expr.data.iteritems():
                if term.head == heads.NUMBER:
                    assert term.data==1,`term.pair` # expected Calculus('1')
                    self.A[i,0] = coeff
                else:
                    try:
                        j = self.names.index(term)
                    except ValueError:
                        j = len(self.names)
                        self.names.append(term)
                    self.A[i,j] = coeff
        else:
            try:
                j = self.names.index(expr)
            except ValueError:
                j = len(self.names)
                self.names.append(expr)
            self.A[i,j] = 1

        self.A = self.A.resize(i+1, len(self.names))

    def show(self):
        print 'A:',', '.join(map(str, self.names))
        print self.A
        print 'L:',self.L
        print 'I:',self.I
