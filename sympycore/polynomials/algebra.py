
from ..core import BasicType
from ..utils import SYMBOL, NUMBER, ADD, MUL, POW
from ..basealgebra.ring import CommutativeRing
from ..basealgebra import PrimitiveAlgebra


class Polynomial(CommutativeRing):

    def __new__(cls, data, variables = None):
        if variables is None:
            raise NotImplementedError(`data`)
        obj = object.__new__(cls)
        assert isinstance(data, PolynomialRing),`data`
        obj.data = data
        obj.variables = variables
        return obj

class PolynomialRingGenerator(BasicType):

    def __getitem__(self, nvars):
        cls = PolynomialRingGenerator('PolynomialRing[%s]' % (nvars), (PolynomialRing,), {})
        cls.nvars = nvars
        return cls
        
class PolynomialRing(CommutativeRing):

    __metaclass__ = PolynomialRingGenerator

    def __new__(cls, data):
        obj = object.__new__(cls)
        obj.data = data
        return obj

    @classmethod
    def convert_coefficient(cls, obj, typeerror=True):
        if isinstance(obj, (int, long, float)):
            data = {(0,)*cls.nvars:obj}
            return cls(data)
        if typeerror:
            raise TypeError('%s.convert_coefficient: failed to convert %s instance'\
                            ' to coefficient algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented

    def as_primitive(self):
        data = self.data
        symbols = [PrimitiveAlgebra((SYMBOL,'X%s' % (i))) for i in range(self.nvars)]
        terms = []
        for exps, coeff in data.iteritems():
            factors = [PrimitiveAlgebra(coeff)]
            for s,e in zip(symbols, exps):
                if e:
                    if e==1:
                        factors.append(s)
                    else:
                        factors.append(s**e)
            terms.append(PrimitiveAlgebra((MUL,tuple(factors))))
        return PrimitiveAlgebra((ADD, tuple(terms)))
                   
        
