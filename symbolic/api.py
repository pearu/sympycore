"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""
__all__ = []

for _n in ['base', 'singleton', 'number', 'symbol', 'power', 'relational', 'mul', 'add', 'apply',
           'ncmul', 'operator', 'function', 'boolean'
           ]:
    exec 'import %s as _m' % (_n)
    __all__ += _m.__all__
    for _s in _m.__all__:
        exec '%s = _m.%s' % (_s, _s)

# creating predefined symbols
for _n, _cls in Symbolic.singleton_classes.items():
    exec '%s = _cls()' % (_n)
    __all__.append(_n)

del _n, _m, _s, _cls

# set repr output to pretty output:
Symbolic.interactive = True
