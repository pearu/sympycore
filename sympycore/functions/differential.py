
from ..core import classes, Expr, init_module
from ..ring import CommutativeRing

init_module.import_heads()
init_module.import_numbers()

class DifferentialRing(CommutativeRing):

    """
    DifferentialRing(DIFF, x) - partial derivative with respect to x
    DifferentialRing(FDIFF, n) - partial derivative with respect to n-th argument
    
    """

    @classmethod
    def convert(cls, obj, typeerror=True):
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, cls.get_value_algebra()):
            return cls(NUMBER, obj)
        return cls.handle_convert_failure('algebra', obj, typeerror)

    def as_algebra(self, cls):
        return NotImplemented

    @classmethod
    def get_apply_algebra(cls):
        return classes.FunctionRing

    @classmethod
    def get_value_algebra(cls):
        return classes.Ring

    def get_differentiation_symbol(self):
        def get_differential_data(cls, head, data, target):
            if head is DIFF or head is FDIFF:
                return data
            return target
        cls = type(self)
        s = self.head.walk(get_differential_data, cls, self.data, self)
        if type(s) is cls:
            raise TypeError('Expression does not contain differential instances')        
        return s

    def __mul__(self, other):
        cls = type(self)
        tother = type(other)
        if tother is not cls:
            if tother in numbertypes_set:
                return self.head.commutative_mul_number(cls, self, other)
            if isinstance(other, type(self.get_differentiation_symbol())):
                return self(other)
            return NotImplemented
        return self.head.commutative_mul(cls, self, other)

    def __rmul__(self, other):
        cls = type(self)
        tother = type(other)
        if tother is not cls:
            if tother in numbertypes_set:
                return self.head.commutative_rmul_number(cls, self, other)
            if isinstance(other, Expr):
                scls = type(d)
                if type(self.get_differentiation_symbol()) is tother:
                    return self.head.non_commutative_rmul_number(cls, self, other)
            return NotImplemented
        return self.head.commutative_mul(cls, self, other)

    def __call__(self, *args):
        cls = type(self)
        if len(args)==1:
            expr = args[0]
            result = self.head.diff_apply(cls, self.data, self, expr)
            if result is not NotImplemented:
                return result
        FAlgebra = self.get_apply_algebra()
        return FAlgebra(APPLY, (self, args))

classes.DifferentialRing = DifferentialRing


class FDFactory(object):

    def __new__(cls, DAlgebra=DifferentialRing, _cache={}):
        obj = _cache.get(DAlgebra)
        if obj is None:
            obj = object.__new__(cls)
            obj.DAlgebra = DAlgebra
            _cache[DAlgebra] = obj
        return obj
    def __str__(self): return 'FD'
    def __repr__(self): return 'FDFactory(%s)' % (self.DAlgebra.__name__)
    def __getitem__(self, index):
        return self.DAlgebra(FDIFF, self.DAlgebra.get_value_algebra()(index))

class DFactory(object):

    def __new__(cls, DAlgebra=DifferentialRing, _cache={}):
        obj = _cache.get(DAlgebra)
        if obj is None:
            obj = object.__new__(cls)
            obj.DAlgebra = DAlgebra
            _cache[DAlgebra] = obj
        return obj
    def __str__(self): return 'D'
    def __repr__(self): return 'DFactory(%s)' % (self.DAlgebra.__name__)
    def __getitem__(self, symbol):
        return self.DAlgebra(DIFF, self.DAlgebra.get_value_algebra()(symbol))
