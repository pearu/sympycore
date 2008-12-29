""" Implementes functions ring support.
"""
#
# Author: Pearu Peterson
# Created: April, 2008
#

__all__ = ['Function', 'FunctionRing', 'D', 'Differential']

from ..core import classes, DefinedFunction, objects, get_nargs
from ..basealgebra import CollectingField, Verbatim, Algebra
from ..utils import SYMBOL, NUMBER, APPLY, DIFF, str_SYMBOL, TERMS, FACTORS
from ..calculus import Calculus

def aseqvalg2str(seq, alg):
    shortname_map = {'Calculus':'Calc'}
    l1 = []
    l2 = []
    for t in seq:
        name = t.__name__
        shortname = shortname_map.get(name, name)
        if l1 and l1[-1]==shortname:
            l2[-1] += 1
        else:
            l1.append(shortname)
            l2.append(1)
    l = []
    for n,e in zip(l1, l2):
        if e==1:
            l.append(n)
        else:
            l.append('%s%s'%(n,e))
    name = alg.__name__
    shortname = shortname_map.get(name, name)
    return '_'.join(l) + '_to_' + shortname

def get_function_ring(aseq, valg):
    name = 'FunctionRing_%s' % (aseqvalg2str(aseq, valg))
    cls = FunctionRingFactory(name, (FunctionRing, ),
                              dict(nargs = len(aseq),
                                   argument_algebras = aseq,
                                   value_algebra = valg
                                   ))
    return cls

objects.get_function_ring = get_function_ring

def Function(obj, *args):
    """ Construct a FunctionRing instance.

    The following signatures are supported:

      Function(name)             - undefined function Calculus->Calculus with name
      Function(name, aseq)       - undefined function aseq->Calculus with name
      Function(name, aseq, valg) - undefined function aseq->valg with name
      Function(call)             - undefined function aseq->Calculus with callable
      Function(call, aseq)       - undefined function aseq->Calculus with callable
      Function(call, aseq, valg) - undefined function aseq->valg with callable
      Function(call, aalg)       - same as Function(call, aseq) where aseq=(aalg,)*nargs
      Function(call, aalg, valg) - same as Function(call, aseq, valg) where aseq=(aalg,)*nargs

    ``aseq`` is a tuple of algebra classes defining the arguments domains of the function.

    ``aalg`` is a algebra class defining the domain of all function arguments.
    
    ``valg`` is a algebra class defining the domain of function values.
    """
    if callable(obj):
        nargs = get_nargs(obj)
    else:
        nargs = 1
    if len(args)==0:
        if isinstance(obj, FunctionRing):
            return obj
        aseq = (classes.Calculus,) * nargs
        valg = classes.Calculus
    elif len(args)==1:
        aseq = args[0]
        if isinstance(aseq, type):
            aseq = (aseq, )*nargs
        valg = classes.Calculus
    elif len(args)==2:
        aseq = args[0]
        if isinstance(aseq, type):
            aseq = (aseq, )*nargs
        valg = args[1]
    else:
        raise TypeError('Function takes 1, 2, or 3 arguments, got %r' % (len(args)+1))
    if not callable(obj):
        nargs = len(aseq)
    else:
        assert nargs==len(aseq)
    cls = get_function_ring(aseq, valg)
    if isinstance(obj, valg): # constant function
        return cls(NUMBER, obj)
    return cls(SYMBOL, obj)   # defined and undefined functions

objects.Function = Function

class FunctionRingFactory(type):
    """ Metaclass for FunctionRing.

    Caches dunamically created classes and implements __getinitargs__
    for pickle support.
    """

    _type_cache = {}

    def __new__(typ, name, bases, attrdict):
        cls = typ._type_cache.get(name)
        if cls is None:
            cls = type.__new__(typ, name, bases, attrdict)
            typ._type_cache[name] = cls
        return cls

    def __getinitargs__(cls):
        # used by pickle support
        attrdict = dict(argument_algebras = cls.argument_algebras,
                        value_algebra = cls.value_algebra,
                        nargs = cls.nargs,
                        )
        return (cls.__name__, cls.__bases__, attrdict)

class FunctionRing(CollectingField):
    """ Base class to functions ring classes.

    Use ``Function`` function to construct instances.
    """

    __metaclass__ = FunctionRingFactory

    argument_algebras = None
    value_algebra = None
    nargs = None

    @classmethod
    def get_predefined_symbols(cls, name):
        if name=='D': return D
        return

    def as_algebra(self, cls):
        if cls is classes.Verbatim:
            return self.as_verbatim()
        if isinstance(self, cls):
            return self.as_verbatim().as_algebra(cls)
        raise TypeError('Cannot convert %s to %s instance' % (type(self).__name__, cls.__name__))

    def __call__(self, *args, **options):
        assert len(args)==self.nargs,`args, self.nargs`
        evaluate = options.get('evaluate', True)
        head, data = self.pair
        if head is NUMBER:
            return self.value_algebra(data)
        args = tuple([t(a) for t, a in zip(self.argument_algebras, args)])
        if head is SYMBOL:
            if callable(data):
                return data(*args)
            f = self.value_algebra.get_defined_function(data)
            if f is not None:
                return f(*args)
        if not evaluate:
            return self.value_algebra.apply(self, *args)
        if head is TERMS:
            return self.value_algebra.Terms(*[(t(*args),c) for t,c in data.iteritems()])
        if head is FACTORS:
            return self.value_algebra.Factors(*[(t(*args),c(*args) if callable(c) else c) for t,c in data.iteritems()])
        return self.value_algebra.apply(self, *args)

    def fdiff(self, index=0):
        return FDiff(self, index)

classes.FunctionRing = FunctionRing

class Differential(CollectingField):
    """ Represents differential algebra.
    """

    @classmethod
    def get_predefined_symbols(cls, name):
        if name=='D': return D
        return

    @classmethod
    def convert(cls, obj, typeerror=True):
        t = type(obj)
        if t is cls:
            return obj
        if t is str:
            obj = Calculus.convert(obj, typeerror)
            if type(obj) is cls:
                return obj
            return cls(NUMBER, obj)
            #return super(CollectingField, cls).convert(obj, typeerror=typeerror)
        return cls(NUMBER, Calculus.convert(obj))

    def __str__(self):
        return self.to_str_data()[1]

    def to_str_data(self, sort=True):
        head, data = self.pair
        if head is SYMBOL:
            return str_SYMBOL, 'D[%s]' % (data)
        return super(type(self), self).to_str_data(sort)
    
    def __call__(self, func):
        func = Function(func)
        cls = type(func)
        return cls.apply(self, func)

class DFactory(object):

    def __new__(cls, _cache=[]):
        if _cache:
            return _cache[0]
        obj = object.__new__(cls)
        _cache.append(obj)
        return obj

    def __str__(self): return 'D'
    def __repr__(self): return 'DFactory()'

    def __getitem__(self, index):
        return Differential(SYMBOL, Calculus.convert(index))

classes.DFactory = DFactory

D = DFactory()
