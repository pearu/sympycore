#
# Author: Pearu Peterson
# Created: February 2008
#

from ..core import BasicType, classes
from ..utils import SYMBOL, NUMBER, ADD, MUL, POW
from ..basealgebra.ring import CommutativeRing
from ..basealgebra import PrimitiveAlgebra

class MatrixRingFactory(BasicType):

    def __new__(typ, name, bases, attrdict):
        if not attrdict.has_key('ring'):
            attrdict['ring'] = classes.Calculus
        if not attrdict.has_key('shape'):
            attrdict['shape'] = None
        cls = type.__new__(typ, name, bases, attrdict)
        cls.zero = cls.Number(0)
        cls.one = cls.Number(1)
        return cls

    def __eq__(self, other):
        if isinstance(other, MatrixRingFactory):
            return self.ring==other.ring and self.shape==other.shape
        return False

    def __ne__(self, other):
        return not self==other

    def __getitem__(self, ring_info, cache={}):
        """ Return a new matrix ring class:

        MatrixRing[<shape>, <coefficient ring>]
        MatrixRing[<shape>] is MatrixRing[<shape>, Calculus]
        MatrixRing[<coefficient ring>] is MatrixRing[None, <coefficient ring>]

        When <shape> is None then shape is determined by the smallest
        and largest index.
        """
        if isinstance(ring_info, (int, long)):
            shape = (ring_info, 1)
            ring = classes.Calculus
        elif isinstance(ring_info, tuple) and isinstance(ring_info[-1], type):
            if len(ring_info)==2:
                shape_info, ring = ring_info
                if isinstance(shape_info, (int, type)):
                    shape = (shape_info, 1)
                elif isinstance(shape_info, (tuple,list)):
                    shape = tuple(shape_info)
                elif shape_info is None:
                    shape = None
                else:
                    raise TypeError(`shape_info, ring_info`)
            else:
                shape = ring_info[:-1]
                ring = ring_info[-1]
        elif isinstance(ring_info, (tuple, list)):
            shape = tuple(ring_info)
            ring = classes.Calculus
        elif ring_info is None:
            shape = None
            ring = classes.Calculus
        else:
            raise TypeError(`ring_info`)

        name = '%s[%s, %s]' % (self.__name__, shape, ring.__name__)
        r = MatrixRingFactory(name,
                              (self,),
                              dict(shape=shape, ring = ring))
        return r

def newinstance(cls, data):
    obj = object.__new__(cls)
    obj.data = data
    return obj


class MatrixRing(CommutativeRing):
    """ Base class to matrix rings that hold matrix element information
    pairs (<indices>: <element>) stored in Python dictionary.
    """


    __slots__ = ['data']

    __metaclass__ = MatrixRingFactory

    def __new__(cls, data):
        if isinstance(data, list):
            data = dict(data)
        elif not isinstance(data, dict):
            return cls.convert(data)
        return newinstance(cls, data)

    def __eq__(self, other):
        return other.__class__ == self.__class__ and self.data == other.data

    @classmethod
    def Number(cls, obj):
        if cls.shape is None:
            return newinstance(cls, {():obj})
        if cls.shape[0]==cls.shape[1]:
            return newinstance(cls, dict([((i,i),obj) for i in range(cls.shape[0])]))
        if cls.shape[0]==1:
            return newinstance(cls, dict([((1,i),obj) for i in range(cls.shape[0])]))
        if cls.shape[1]==1:
            return newinstance(cls, dict([((i,1),obj) for i in range(cls.shape[0])]))
        raise NotImplementedError(`cls.shape, obj`)

    def __str__(self):
        return '['+', '.join(['(%s, %s)' % (i,e) for i,e in self.data.iteritems()])+']'

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data.get(key, 0)

    def __mul__(self, other):
        if isinstance(other, MatrixRing) and self.shape[-1]==other.shape[0] and self.ring==other.ring:
            return mul_MATRIX_MATRIX(self, other)
        return NotImplemented

def mul_MATRIX_MATRIX(lhs, rhs):
    cls = MatrixRing[(lhs.shape[0], rhs.shape[-1]), lhs.ring]
    d = {}
    r = newinstance(cls, d)
    raise NotImplementedError
    return r
