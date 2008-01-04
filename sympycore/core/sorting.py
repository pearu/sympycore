
import types

from .utils import singleton
from .basic import classes

__all__ = ['sort_sequence']

ordering_of_classes = [
    'Number','MathematicalSymbol',
    'BasicSymbol','Atom',
    'BasicFunction','Callable',
    'Composite',
    'Basic',
    ]

def sort_sequence(seq):
    """ Sorts a sequence of Basic instances:
    - first by the class index of an item defined in ordering_of_classes list,
    - second by the number of operations in an item,
    - third by the class name of an item,
    - and finally, using the class compare method.
    """
    #The class compare method should return -1, 0, or 1. The method is
    #guaranteed to have arguments of exactly the same classes. If the
    #class (or its parent class) does not define compare method then
    #the default cmp will be used (ie id comparison).
    return sort_by_class_order(seq)

def sort_template(seq, functional, subsort):
    d = {}
    for obj in seq:
        n = functional(obj)
        if not d.has_key(n):
            d[n] = []
        d[n].append(obj)
    r = []
    for k in sorted(d.keys()):
        r += subsort(d[k])
    return r

@singleton
def get_class_index(cls):
    clsbase = None
    clsindex = -len(ordering_of_classes)
    for i in range(len(ordering_of_classes)):
        basename = ordering_of_classes[i]
        base = getattr(classes, basename, None)
        if base is None:
            base = getattr(types, basename, object)
        if issubclass(cls, base):
            if clsbase is None:
                clsbase, clsindex = base, i
            else:
                if issubclass(base, clsbase):
                    clsbase,clsindex = base, i #pragma NO COVER
    return clsindex

class_order_func = lambda obj: get_class_index(obj.__class__)
nofops_func = lambda obj: obj.count_ops(symbolic=False)
class_func = lambda obj: obj.__class__

def sort_by_class_order(seq):
    return sort_template(seq, class_order_func, sort_by_nofops)

def sort_by_nofops(seq):
    return sort_template(seq, nofops_func, sort_by_class)

def sort_by_class(seq):
    return sort_template(seq, class_func, sort_by_class_compare)

def sort_by_class_compare(seq):
    # all items in seq will be of the same class as submitted
    # by the sort_by_class method.
    return sorted(seq, cmp=lambda x,y: x.compare(y))

