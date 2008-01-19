
from ..core import sympify, classes
from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL

from .pairs import CommutativeRingWithPairs

from .numberlib import mpq, mpf, mpc, try_power, extended_number, undefined

algebra_numbers = (int, long, float, complex, mpq, mpf, mpc, extended_number)

class StandardCommutativeAlgebra(CommutativeRingWithPairs):
    """ Represents an element of a symbolic algebra. The set of a
    symbolic algebra is a set of expressions. There are four kinds of
    expressions: Symbolic, SymbolicNumber, SymbolicTerms,
    SymbolicFactors.

    StandardCommutativeAlgebra basically models the structure of SymPy.
    """

    __slots__ = ['head', 'data', '_hash', 'one', 'zero']
    _hash = None

    @classmethod
    def redirect_operation(cls, *args, **kws):
        """ Default implementation of redirect_operation method
        used as a callback when RedirectOperation exception is raised.
        """
        callername = kws['redirect_operation']
        flag = True
        if callername=='__mul__':
            lhs, rhs = args
        elif callername=='__rmul__':
            rhs, lhs = args
        else:
            flag = False
        if flag:
            if isinstance(rhs, cls) and rhs.head is NUMBER:
                if rhs.data == undefined:
                    return rhs
            if isinstance(lhs, cls) and lhs.head is NUMBER:
                if lhs.data == undefined:
                    return lhs
            
        return getattr(cls, callername)(*args,
                                        **dict(redirect_operation='ignore_redirection'))            

            

    @classmethod
    def convert_coefficient(cls, obj, typeerror=True):
        """ Convert obj to coefficient algebra.
        """
        if isinstance(obj, algebra_numbers):
            return obj
        if typeerror:
            raise TypeError('%s.convert_coefficient: failed to convert %s instance'\
                            ' to coefficient algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented
    
    @classmethod
    def Number(cls, num, denom=None):
        if denom is None:
            return cls(num, head=NUMBER)
        return cls(mpq(num, denom), head=NUMBER)

    @classmethod
    def Symbol(cls, obj):
        return cls(obj, head=SYMBOL)

    @classmethod
    def convert_exponent(cls, obj, *args):
        if isinstance(obj, cls):
            return obj
        return cls(obj)

    @classmethod
    def Pow(cls, base, exp):
        if exp is -1 and base.head is NUMBER:
            # fast path for division
            return cls(try_power(base.data, -1)[0], head=NUMBER)
        N = cls.Number
        exp = cls.convert(exp)
        if base.head is NUMBER and exp.head is NUMBER:
            num, sym = try_power(base.data, exp.data)
            if not sym:
                return N(num)
            base, exp = sym
            sym = cls({N(base):N(exp)}, head=MUL)
            if num == 1:
                return sym
            return cls({sym:N(num)}, head=ADD)
        if exp == 0:
            return cls.one
        if exp == 1 or cls.one==base:
            return base
        return cls({base:exp}, head=MUL)

one = StandardCommutativeAlgebra(1, head=NUMBER)
zero = StandardCommutativeAlgebra(0, head=NUMBER)
I = StandardCommutativeAlgebra(mpc(0,1), head=NUMBER)

StandardCommutativeAlgebra.one = one
StandardCommutativeAlgebra.zero = zero
