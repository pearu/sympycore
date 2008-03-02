"""Provides Basic class and classes object.
"""

__docformat__ = 'restructuredtext'
__all__ = ['classes', 'APair']

try:
    from .apair_ext import APair
except ImportError:
    from .apair import APair

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
#objects = Holder('Sympy predefined objects holder (%(_counter)s objects)')

