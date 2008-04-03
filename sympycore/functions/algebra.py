""" Implementes functions ring support.
"""
#
# Author: Pearu Peterson
# Created: April, 2008
#

__all__ = ['Function', 'FunctionRing']

from ..core import classes
from ..basealgebra import CollectingField, Verbatim
from ..utils import SYMBOL, NUMBER, APPLY

def Function(obj, *args):
    """ Construct a FunctionRing instance.

    The following signatures are supported:

      Function(name)             - undefined function Calculus->Calculus with name
      Function(name, aseq)       - undefined function aseq->Calculus with name
      Function(name, aseq, valg) - undefined function aseq->valg with name
      Function(call)             - undefined function aseq->Calculus with callable
      Function(call, aseq)       - undefined function aseq->Calculus with callable
      Function(call, aseq, valg) - undefined function aseq->valg with callable

    ``aseq`` is a tuple of algebra classes or a algebra class defining the
    arguments domains of the function.
    
    ``valg`` is a algebra class defining the domain of function values.
    """
    if len(args)==0:
        if isinstance(obj, FunctionRing):
            return obj
        if callable(obj):
            raise NotImplementedError('get nofargs from callable')
        aseq = (classes.Calculus,)
        valg = classes.Calculus
    elif len(args)==1:
        if callable(obj):
            raise NotImplementedError('check nofargs of callable')
        aseq = args[0]
        valg = classes.Calculus
    elif len(args)==2:
        if callable(obj):
            raise NotImplementedError('check nofargs of callable')
        aseq = args[0]
        valg = args[1]
    else:
        raise TypeError('Function takes 1, 2, or 3 arguments, got %r' % (len(args)+1))

    name = 'FunctionRing_%s_to_%s' % ('_'.join([t.__name__ for t in aseq]), valg.__name__)
    cls = FunctionRingFactory(name, (FunctionRing, ),
                              dict(nargs = len(aseq),
                                   argument_algebras = aseq,
                                   value_algebra = valg
                                   ))
    if isinstance(obj, valg): # constant function
        return cls(NUMBER, obj)
    return cls(SYMBOL, obj)   # defined and undefined functions

class FunctionRingFactory(type):

    _type_cache = {}

    def __new__(typ, name, bases, attrdict):
        cls = typ._type_cache.get(name)
        if cls is None:
            cls = type.__new__(typ, name, bases, attrdict)
            typ._type_cache[name] = cls
        return cls

    def __getinitargs__(cls):
        attrdict = dict(argument_algebras=cls.argument_algebras,
                        value_algebra = cls.value_algebra,
                        nargs = cls.nargs,
                        )
        return (cls.__name__, cls.__bases__, attrdict)

class FunctionRing(CollectingField):
    """ Base class to Map classes.

    Use ``Function`` function to construct instances.
    """

    __metaclass__ = FunctionRingFactory

    argument_algebras = None
    value_algebra = None
    nargs = None

    def as_algebra(self, cls):
        if cls is classes.Verbatim:
            return self.as_verbatim()
        if isinstance(self, cls):
            return self.as_verbatim().as_algebra(cls)
        raise TypeError('Cannot convert %s to %s instance' % (type(self).__name__, cls.__name__))

    def __call__(self, *args):
        assert len(args)==self.nargs,`args, self.nargs`
        args = tuple([t(a) for t, a in zip(self.argument_algebras, args)])
        return self.value_algebra(self, args)
