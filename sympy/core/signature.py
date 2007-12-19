
from .basic import classes, Basic

__all__ = ['FunctionSignature']

class FunctionSignature:
    """
    Function signature defines valid function arguments
    and its expected return values.

    Examples:

    A function with undefined number of arguments and return values:
    >>> f = Function('f', FunctionSignature(None, None))

    A function with undefined number of arguments and one return value:
    >>> f = Function('f', FunctionSignature(None, (Basic,)))

    A function with 2 arguments and a pair in as a return value,
    the second argument must be Python integer:
    >>> f = Function('f', FunctionSignature((Basic, int), (Basic, Basic)))

    A function with one argument and one return value, the argument
    must be float or int instance:
    >>> f = Function('f', FunctionSignature(((float, int), ), (Basic,)))

    A function with undefined number of Basic type arguments and return values:
    >>> f = Function('f', FunctionSignature([Basic], None))
    """

    def __init__(self, argument_classes = (Basic,), value_classes = (Basic,)):
        self.argument_classes, self.nof_arguments = self._normalize(argument_classes, 1)
        self.value_classes, self.nof_values = self._normalize(value_classes, 2)

    @staticmethod
    def _normalize(classes, i):
        if isinstance(classes, type):
            classes = (classes,)
        nof_classes = None
        if classes is not None:
            if isinstance(classes, tuple):
                nof_classes = len(classes)
            elif isinstance(classes, list):
                classes = tuple(classes)
            else:
                raise TypeError('FunctionSignature: wrong argument[%s] type %s, expected NoneType|tuple|list|type' % (i, type(classes).__name__))
        return classes, nof_classes

    @staticmethod
    def _validate(funcname, values, intentname, value_classes, nof_values):
        if nof_values is not None:
            if nof_values!=len(values):
                return ('function %s: wrong number of %ss, expected %s, got %s'\
                        % (funcname, intentname, nof_values, len(values)))
            i = 0
            for a,cls in zip(values, value_classes):
                i += 1
                if not isinstance(a, cls):
                    if isinstance(cls, tuple):
                        clsinfo = '|'.join([c.__name__ for c in cls])
                    else:
                        clsinfo = cls.__name__
                    return ('function %s: wrong %s[%s] type %r, expected %r'\
                            % (funcname, intentname, i, type(a).__name__, clsinfo))
        elif value_classes is not None:
            i = 0
            for a in values:
                i += 1
                if not isinstance(a, value_classes):
                    clsinfo = '|'.join([c.__name__ for c in value_classes])
                    return ('function %s: wrong %s[%s] type %r, expected %r'\
                            % (funcname, intentname, i, type(a).__name__, clsinfo))

    def validate(self, funcname, args):
        return self._validate(funcname, args, 'argument', self.argument_classes, self.nof_arguments)

    def validate_return(self, funcname, results):
        return self._validate(funcname, results, 'return', self.value_classes, self.nof_values)

    def __repr__(self):
        if self.nof_arguments is None and self.argument_classes is not None:
            arg1 = [self.argument_classes]
        else:
            arg1 = self.argument_classes
        if self.nof_values is None and self.value_classes is not None:
            arg2 = [self.value_classes]
        else:
            arg2 = self.value_classes
        return '%s(%r, %r)' % (self.__class__.__name__, arg1, arg2)

classes.FunctionSignature = FunctionSignature
