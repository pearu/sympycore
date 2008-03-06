"""Provides Basic class and classes object.
"""

__docformat__ = 'restructuredtext'
__all__ = ['classes', 'Expr']

using_C_Expr = False
try:
    from .expr_ext import Expr
    using_C_Expr = True
except ImportError, msg:
    msg = str(msg)
    if msg!='No module named expr_ext':
        print msg
    from .expr import Expr

# Pickling support:
from .utils import get_head
def _reconstruct(version, state):
    # Used in <Expr instance>.__reduce__
    if version==1:
        cls, (head, data), hashvalue = state
        head = get_head(head)
        obj = cls(head, data)
        obj._sethash(hashvalue)
        return obj
    raise NotImplementedError('pickle _reconstruct version=%r' % (version))

if using_C_Expr:
    # To add support pickling pure Expr instances, uncomment the
    # following line (but it is hackish):
    #
    #__builtins__['Expr'] = Expr
    #
    # Pickling Python classes derived from Expr should work fine
    # without this hack.
    pass

class Holder:
    """ Holds pairs ``(name, value)`` as instance attributes.
    
    The set of pairs is extendable via setting

    ::
    
      <Holder instance>.<name> = <value>
    """
    def __init__(self, descr):
        self._descr = descr
        self._counter = 0

    def __str__(self):
        return self._descr % (self.__dict__)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))
    
    def __setattr__(self, name, obj):
        if not self.__dict__.has_key(name) and self.__dict__.has_key('_counter'):
            self._counter += 1
        self.__dict__[name] = obj

    def iterNameValue(self):
        for k,v in self.__dict__.iteritems():
            if k.startswith('_'):
                continue
            yield k,v


classes = Holder('Sympy Basic subclass holder (%(_counter)s classes)')
classes.Expr = Expr
#objects = Holder('Sympy predefined objects holder (%(_counter)s objects)')

