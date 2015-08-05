"""
Symbolic - base class for symbolic objects.

Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: 2006
"""

import re
import sys
import types
import decimal

__all__ = ['Symbolic', 'Range']

integer_types = (int, long)
decimal_types = integer_types + (decimal.Decimal, float)

sorted_classes = [ # Used in canonical ordering of symbolic
                   # sequences via compare method.
    'NaN',
    'Infinity',
    'Zero','One',
    'ImaginaryUnit',
    'Integer','Rational','Decimal','Pi','Exp1',
    'DummySymbol','Symbol','Apply','Power','NcMul','Mul','Add', 
    'Exp','Log','Ln','Sin','Cos',
    'SymbolicFunction',
    'UndefinedFunction',
    'Differential','IndefinedIntegral','DefinedIntegral',
    'NegativeInfinity',
    'NegativeOne',
    'NegativeImaginaryUnit',
    'Half',
    'Equal','NotEqual','Less','LessEqual','Greater','GreaterEqual',
    'Not','And','XOr','Or',
    ]


class AttributeHolder:
    """
    Defines a object with predefined attributes. Only those attributes
    are allowed that are specified as keyword arguments of a constructor.
    When an argument is callable then the corresponding attribute will
    be read-only and set by the value the callable object returns.
    """
    def __init__(self, **kws):
        self._attributes = {}
        self._readonly = []
        for k,v in kws.items():
            self._attributes[k] = v
            if callable(v):
                self._readonly.append(k)
        return

    def __getitem__(self, key):
        if isinstance(key, tuple):
            name, args = key
        else:
            name = key
            args = ()
        attrs = self._attributes
        value = attrs[name]
        if callable(value) and not isinstance(value, Symbolic):
            if args:
                if attrs.has_key(key):
                    value = attrs[key]
                else:
                    value = value(*args)
                    attrs[key] = value
            else:
                value = value()
                attrs[key] = value
        return value

    def __getattr__(self, name):
        fullname = name
        if ',' in name:
            l = name.split(',')
            name = l[0]
            args = tuple(l[1:])
        else:
            args = ()
        attrs = self._attributes
        if name not in attrs:
            raise AttributeError,'%s instance has no attribute %r, '\
                  'expected attributes: %s' \
                  % (self.__class__.__name__,name,
                     ','.join(attrs.keys()))
        return self[name,args]
        value = attrs[name]
        if callable(value) and not isinstance(value, Symbolic):
            if args:
                if attrs.has_key(fullname):
                    value = attrs[fullname]
                else:
                    value = value(*args)
            else:
                value = value()
            attrs[fullname] = value
        return value

    def __setattr__(self, name, value):
        if name in ['_attributes','_readonly']:
            self.__dict__[name] = value
            return
        if name in self._readonly:
            raise AttributeError,'%s instance attribute %r is readonly' \
                  % (self.__class__.__name__, name)
        if name not in self._attributes:
            raise AttributeError,'%s instance has no attribute %r, '\
                  'expected attributes: %s' \
                  % (self.__class__.__name__,name,','.join(self._attributes.keys()))
        self._attributes[name] = value

    def __repr__(self):
        l = []
        for k in self._attributes.keys():
            v = getattr(self,k)
            l.append('%s=%r' % (k,v))
        return '%s(%s)' % (self.__class__.__name__,', '.join(l))

#
# End of AttributeHolder class
#
################################################################################


class BooleanMethods(object):

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self): return Symbolic.Not(self)
    def __and__(self, other): return Symbolic.And(self, other)
    def __or__(self, other): return Symbolic.Or(self, other)
    def __xor__(self, other): return Symbolic.XOr(self, other)
    def implies(self, other): return (~self) | Symbolic(other)
    def equiv(self, other): return ~ (self ^ Symbolic(other))

#
# End of BooleanMethods class
#
################################################################################


class RelationalMethods(object):

    ############################################################################
    #
    # Relational methods
    #
    
    def __eq__(self, other): return Symbolic.Equal(self, other)
    def __ne__(self, other): return Symbolic.NotEqual(self, other)
    def __lt__(self, other): return Symbolic.Less(self, other)
    def __gt__(self, other): return Symbolic.Less(other, self)
    def __le__(self, other): return Symbolic.LessEqual(self, other)
    def __ge__(self, other): return Symbolic.LessEqual(other, self)

#
# End of RelationalMethods class
#
################################################################################


class ArithmeticMethods(object):

    ############################################################################
    #
    # Arithmetic operations
    #

    def __pos__(self): return self
    def __neg__(self): return Symbolic.Mul(Symbolic.NegativeOne(), self)
    def __add__(self, other): return Symbolic.Add(self, other)
    def __radd__(self, other): return Symbolic(other) + self
    def __mul__(self, other): return Symbolic.Mul(self, other)
    def __rmul__(self, other): return Symbolic(other) * self
    def __sub__(self, other): return self + (-Symbolic(other))
    def __rsub__(self, other): return Symbolic(other) - self
    def __pow__(self, other): return Symbolic.Power(self, other)
    def __rpow__(self, other): return Symbolic(other) ** self
    def __div__(self, other): return self * (Symbolic(other) ** Symbolic.NegativeOne())
    def __rdiv__(self, other): return Symbolic(other) * (self**Symbolic.NegativeOne())

    def ncmul(self, other): return Symbolic.NcMul(self, other)
    def ncdiv(self, other): return Symbolic.NcMul(self, Symbolic(other)**Symbolic.NegativeOne())

    ###########################################################################
    #
    # Comparison methods
    #

    def is_less(self, other):
        r = (self - other).expand()
        if isinstance(r, Symbolic.Number):
            return r.is_negative()
        return None

#
# End of ArithmeticMethods class
#
################################################################################


class FunctionalMethods(object):

    ############################################################################
    #
    # Functional methods
    #
    
    def __call__(self, *args):
        return Symbolic.Apply(self, *args)

    def calc_diff(self, *args):
        # All calc_diff() methods must start with the following line:
        if not args: return self.calc_diff
        if len(args)>1: return self.calc_diff(args[0]).diff(*args[1:])
        #
        return Symbolic.Differential(args[0])(self).diff(*args[1:])

    def diff(self, *args):
        if not args: return self
        args = tuple(map(Symbolic, args))
        return self.flags['diff',args]

    def calc_integrate(self, *args):
        if not args: return self.calc_integrate
        if len(args)>1: return self.calc_integrate(args[0]).integrate(*args[1:])
        a = Symbolic(args[0])
        if isinstance(a, Symbolic.Range):
            op = Symbolic.Integral(a.coeff, a.seq[0], a.seq[1])
        else:
            op = Symbolic.Integral(a) #+ IC(a)
        return Symbolic.Apply(op, self)

    def integrate(self, *args):
        if not args: return self
        args = tuple(map(Symbolic, args))
        return self.flags['integrate',args]

#
# End of FunctionalMethods class
#
################################################################################


class Symbolic(object):
    """ Base class for symbolic objects.
    
    Notes:
      Derived classes will set themself as attributes of Symbolic class.
      For example, Symbolic.Number, Symbolic.Add etc.
    """

    interactive = False        # defines the output of repr()
    singleton_classes = {}     # singleton class mapping

    ############################################################################
    # Static methods
    #
    
    def get_Symbolic_namespace():
        """
        Return a variable with name Symbolic_namespace in parent frames.
        """
        frame = sys._getframe(1)
        frames = [frame]
        while frame is not None:
            namespace = frame.f_locals.get('Symbolic_namespace', None)
            if namespace is not None:
                for frame in frames:
                    frame.f_locals['Symbolic_namespace'] = namespace
                return namespace
            try:
                name = frame.f_locals['__name__']
            except KeyError:
                name = None
            if name is not None and name=='__main__':
                #exec('Symbolic_namespace = {}', frame.f_globals, frame.f_locals)
                namespace = frame.f_locals['Symbolic_namespace'] = {}
                for frame in frames:
                    frame.f_locals['Symbolic_namespace'] = namespace

                return namespace
            frames.append(frame)
            frame = frame.f_back
        return Symbolic.Symbolic_namespace
    get_Symbolic_namespace = staticmethod(get_Symbolic_namespace)
    
    Symbolic_namespace = {} # default return value for get_Symbolic_namespace

    #

    def _apply_mth(mthname, lst, args = ()):
        """
        For objects in lst call mthname with args and return (flag, new_lst)
        where new_lst contains the returned values and flag is True whenever
        new_lst != lst.
        """
        flag = False
        new_lst = []
        for p in lst:
            p1 = getattr(p, mthname)(*args)
            flag = flag or p1 is not p
            new_lst.append(p1)
        return flag, new_lst

    _apply_mth = staticmethod(_apply_mth)

    #

    def process_lambda_args(lambda_args, t):
        
        if isinstance(t, Symbolic.DefinedFunction):
            args = t.get_dummy_symbols()
            expr = t.get_expression()
            if lambda_args is None:
                lambda_args = args
                t = expr
            else:
                if len(lambda_args) != len(args):
                    raise ValueError,'cannot operate lambda functions with'\
                          ' different number of arguments: expected %s but got %s' \
                          % (len(lambda_args), len(args))
                if lambda_args==args:
                    t = expr
                else:
                    e = expr
                    s12_list = []
                    for s1, s2 in zip(args, lambda_args):
                        if s1 in lambda_args:
                            s12 = Symbolic.Symbol()
                            e = e.substitute(s1, s12)
                            s12_list.append((s12, s2))
                        else:
                            e = e.substitute(s1, s2)
                    for s12,s2 in s12_list:
                        e = e.substitute(s12, s2)
                    t = e

        return lambda_args, t

    process_lambda_args = staticmethod(process_lambda_args)

    #

    def set_precision(prec = None):
        """
        Set precision for Decimal number operations and return previous precision value.
        """
        context = decimal.getcontext()
        oldprec = context.prec
        if prec is not None:
            context.prec = prec
        return oldprec

    set_precision = staticmethod(set_precision)

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls, *args, **kws):
        if cls is Symbolic:
            assert not kws
            assert len(args)==1
            obj = args[0]
            if isinstance(obj, Symbolic):
                return obj
            if isinstance(obj, bool):
                if obj: return Symbolic.TRUE()
                return Symbolic.FALSE()
            if isinstance(obj, integer_types):
                return Symbolic.Number(obj)
            elif isinstance(obj, decimal_types):
                return Symbolic.Decimal(obj)
            if isinstance(obj, str):
                namespace = Symbolic.get_Symbolic_namespace()
                try:
                    return namespace[obj]
                except KeyError:
                    obj1 = namespace[obj] = parser.Expr(obj).tosymbolic()
                    return obj1
            raise TypeError,`type(obj)`
        obj = object.__new__(cls)
        
        expected_nof_args = obj.init.im_func.func_code.co_argcount-1
        if expected_nof_args != len(args):
            raise TypeError,'%s.init() takes exactly %s arguments (%s given)' \
                  % (cls.__name__, expected_nof_args, len(args))

        obj.init(*args)
        
        for k,f in kws.items():
            if isinstance(f,types.MethodType) and f.im_self is None:
                # f is unbound method
                kws[k] = lambda f=f,obj=obj: f(obj)
        
        if isinstance(obj, Symbolic.Rational):
            kws['factors'] = obj.calc_factors
        if isinstance(obj, FunctionalMethods):
            kws['diff'] = obj.calc_diff
            kws['integrate'] = obj.calc_integrate
            
        obj.flags = AttributeHolder(\
                                    expanded=obj.calc_expanded,
                                    symbols=obj.calc_symbols,
                                    free_symbols=obj.calc_free_symbols,
                                    hash=obj.calc_hash,
                                    todecimal = obj.calc_todecimal,
                                    **kws)

        return obj

    def init(self,*args, **kws):
        """ Initialize Symbolic object.
        """
        raise NotImplementedError,'%s needs init() method' % (self.__class__.__name__)

    def astuple(self):
        """ Return class name and constructor arguments.
        """
        raise NotImplementedError,'%s needs astuple() method' \
              % (self.__class__.__name__)

    def eval_power(base, exponent):
        """ Evaluate Power(self, other), return new object or None if
        no evaluation can be carried out.
        """
        print 'WARNING: %s does not define .eval_power() method' % (base.__class__)
        return

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self):
        print 'WARNING: %s does not define .get_precedence() method' % (self.__class__)
        return 0

    def calc_hash(self):
        """ Return hash value of the object. It's value
        is saved as self.flags.hash.
        """
        return hash(self.astuple())

    def __hash__(self):
        return self.flags.hash

    def calc_symbols(self):
        """ Find all symbols contained in the object.
        """
        r = set()
        for s in self.astuple()[1:]:
            if isinstance(s, Symbolic):
                r.update(s.symbols())
            elif isinstance(s, str):
                pass
            else:
                print 'WARNING: %s.calc_symbols() may be incomplete (don\'t know about %r)' \
                      % (self.__class__.__name__, type(s))
        return r

    def symbols(self):
        return self.flags.symbols

    def calc_free_symbols(self):
        """ Find free symbols of the expression. Different from
        calc_symbols(), definite integration variables and function names are skipped.
        """
        r = set()
        for s in self.astuple()[1:]:
            if isinstance(s, Symbolic):
                r.update(s.free_symbols())
            elif isinstance(s, str):
                pass
            else:
                print 'WARNING: %s.calc_free_symbols() may be incomplete (don\'t know about %r)' \
                      % (self.__class__.__name__, type(s))
        return r

    def free_symbols(self):
        return self.flags.free_symbols

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        print 'WARNING: %s does not define .tostr() method' % (self.__class__)
        return self.torepr()

    def torepr(self):
        t = self.astuple()
        l = []
        for o in t[1:]:
            try:
                l.append(o.torepr())
            except AttributeError:
                l.append(repr(o))
        return t[0] + '(' + ', '.join(l) + ')'        

    def __repr__(self):
        if Symbolic.interactive:
            return 'Symbolic(%r)' % (self.tostr())
        return self.torepr()

    def calc_todecimal(self, *args):
        """ Return all numbers in symbolic object to Decimal numbers. 
        """
        if not args:
            return self.calc_todecimal
        flag, new_seq = self._apply_mth('todecimal', self.astuple()[1:])
        if flag:
            return self.__class__(*new_seq)
        return self



    def todecimal(self):
        return getattr(self.flags,'todecimal,%s' % (Symbolic.set_precision()))

    def calc_expanded(self):
        """ Perform expansion of the object.
        """
        flag, new_seq = self._apply_mth('expand', self.astuple()[1:])
        if flag:
            return self.__class__(*new_seq)
        return self

    def expand(self):
        return self.flags.expanded


    ###########################################################################
    #
    # Comparison methods
    #
    
    def compare_classes(self, other):
        n1 = self.__class__.__name__
        n2 = other.__class__.__name__
        c = cmp(n1,n2)
        if not c: return 0
        try:
            i1 = sorted_classes.index(n1)
        except ValueError:
            print 'Add',n1,'to symbolic.base.sorted_classes'
            return c
        try:
            i2 = sorted_classes.index(n2)
        except ValueError:
            print 'Add',n2,'to symbolic.base.sorted_classes'
            return c
        return cmp(i1,i2)

    def compare(self, other):
        """
        Return -1,0,1 if the object is smaller, equal, or greater than other.
        If the object is of different type from other then their classes
        are ordered according to sorted_classes list.
        """
        # all redefinitions of compare method should start with the
        # following three lines:
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        #
        if not self.__class__.compare==Symbolic.compare:
            return self.compare(other)
        st = self.astuple()
        ot = other.astuple()
        c = cmp(len(st),len(ot))
        if c: return c
        for l,r in zip(st,ot)[1:]:
            c = l.compare(r)
            if c: return c
        return 0

    def __cmp__(self, other):
        return self.compare(other)

    def is_equal(self, other):
        """
        Return True if objects are equal.
        Return False if objects are not equal.
        Return None if the equality of objects can be either True or False.
        """
        assert isinstance(other, Symbolic),`other`
        if not self.compare(other):
            return True
        if isinstance(self, ArithmeticMethods) and isinstance(other, ArithmeticMethods):
            r = (self - other).expand()
            if isinstance(r, Symbolic.Zero): return True
            if isinstance(r, Symbolic.Number): return False
            return None
        if isinstance(self, BooleanMethods) and isinstance(other, BooleanMethods):
            r = (self.implies(other) & other.implies(self)).expand()
            if isinstance(r, Symbolic.TRUE): return True
            if isinstance(r, Symbolic.FALSE): return False
            return None
        return None

    ###########################################################################
    #
    # Auxiliary methods
    #

    def is_in(self, seq):
        """ Return True if object is in sequence seq. Does not use == operation.
        """
        for s in seq:
            if not self.compare(s):
                return True
        return False

    def index_in(self, seq):
        """ Return object index in seq.
        """
        i = 0
        for s in seq:
            if self.compare(s):
                i += 1
                continue
            return i
        raise ValueError,'%s.index_in(seq): object not in seq' % (self.__class__)

    def remove_in(self, seq):
        """ Remove object from seq. seq must be mutable.
        """
        i = 0
        lst = []
        for s in seq:
            if self.compare(s):
                i += 1
                continue
            lst.append(i)
        lst.reverse()
        for i in lst:
            del seq[i]
        return

    ############################################################################
    #
    # Substitution methods
    #

    def calc_substitute(self, subst, replacement):
        flag, new_seq = self._apply_mth('substitute', self.astuple()[1:], (subst, replacement))
        if flag:
            return self.__class__(*new_seq)
        return self

    def _process_substitute_args(subst, replacement):
        if replacement is None:
            assert isinstance(subst, Symbolic.Keyword),`subst`
            replacement = subst.rhs
            subst = subst.lhs
        else:
            replacement = Symbolic(replacement)
            subst = Symbolic(subst)        
        return subst, replacement

    _process_substitute_args = staticmethod(_process_substitute_args)

    def substitute(self, subst, replacement=None):
        """
        Substitute subst with replacement in symbolic expression.
        """
        subst, replacement = self._process_substitute_args(subst, replacement)
        if self.is_equal(subst):
            return replacement
        if isinstance(subst, Symbolic.SymbolBase) and subst not in self.symbols():
            return self
        return self.calc_substitute(subst, replacement)

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self):
        raise TypeError,'unary operation `~` not defined for %s' % (self.__class__.__name__)
    def __and__(self, other):
        raise TypeError,'binary operation `&` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def __xor__(self, other):
        raise TypeError,'binary operation `^` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def __or__(self, other):
        raise TypeError,'binary operation `|` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def implies(self, other):
        raise TypeError,'binary operation `->` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def equiv(self, other):
        raise TypeError,'binary operation `<=>` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    
    ############################################################################
    #
    # Relational methods
    #
    
    def __eq__(self, other):
        raise TypeError,'binary operation `==` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def __ne__(self, other):
        raise TypeError,'binary operation `!=` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def __lt__(self, other):
        raise TypeError,'binary operation `<` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def __gt__(self, other):
        raise TypeError,'binary operation `>` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def __le__(self, other):
        raise TypeError,'binary operation `<=` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def __ge__(self, other):
        raise TypeError,'binary operation `>=` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)

    ############################################################################
    #
    # Arithmetic operations
    #

    def __pos__(self):
        raise TypeError,'unary operation `+` not defined for %s' % (self.__class__.__name__)
    def __neg__(self):
        raise TypeError,'unary operation `-` not defined for %s' % (self.__class__.__name__)
    def __add__(self, other):
        raise TypeError,'binary operation `+` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    __radd__ = __add__
    def __mul__(self, other):
        raise TypeError,'binary operation `*` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    __rmul__ = __mul__
    def __sub__(self, other):
        raise TypeError,'binary operation `-` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    __rsub__ = __sub__
    def __pow__(self, other):
        raise TypeError,'binary operation `-` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    __rpow__ = __pow__
    def __div__(self, other):
        raise TypeError,'binary operation `-` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    __rdiv__ = __div__
    def ncmul(self, other):
        raise TypeError,'binary operation nc`*` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)
    def ncdiv(self, other):
        raise TypeError,'binary operation nc`/` not defined between %s and %s' \
              % (self.__class__.__name__, other.__class__.__name__)


    ############################################################################
    #
    # Functional methods
    #

    def __call__(self, *args):
        raise TypeError,'%s is not callable' % (self.__class__.__name__)


    def diff(self, *args):
        raise TypeError,'%s is not differentiable' % (self.__class__.__name__)
    calc_diff = diff

    def integrate(self, *args):
        raise TypeError,'%s is not integrable' % (self.__class__.__name__)
    calc_integrate = integrate

#
# End of Symbolic class
#
################################################################################



class Constant(FunctionalMethods, Symbolic):
    """ Base class for numbers and symbolic constants.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1
        """
        return

    ############################################################################
    #
    # Informational methods
    #

    def calc_symbols(self): return set()

    def calc_free_symbols(self): return set()

    def calc_diff(self, *args):
        # All calc_diff() methods must start with the following two lines:
        if not args: return self.calc_diff
        #if len(args)>1: return self.calc_diff(args[0]).diff(*args[1:])
        #
        return Symbolic.Zero()

    def calc_integrate(self, *args):
        # All calc_diff() methods must start with the following two lines:
        if not args: return self.calc_integrate
        if len(args)>1: return self.calc_integrate(args[0]).integrate(*args[1:])
        a = args[0]
        if isinstance(a, Symbolic.Range):
            return (a.seq[1] - a.seq[0]) * self
        else:
            return a * self

#
# End of Constant class
#
################################################################################


class SymbolicSequence(Symbolic):
    """ Base class for symbolic sequences.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls,*seq):
        raise NotImplementedError,'%s must define __new__ method' % (cls)

    def init(self, coeff, seq):
        self.coeff = coeff
        self.seq = tuple(seq)
        return

    def astuple(self):
        return (self.__class__.__name__, self.coeff)+self.seq

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 10

    ###########################################################################
    #
    # Transformation methods
    #

    def seqtostr(self, delim, this_precedence, upper_precedence):
        if not self.seq:
            r = self.coeff.tostr(this_precedence)
        elif hasattr(self.__class__,'identity') and self.coeff==self.identity:
            r = delim.join([s.tostr(this_precedence) for s in self.seq])
        else:
            r = delim.join([s.tostr(this_precedence) for s in (self.coeff,) + self.seq])
        if this_precedence<=upper_precedence:
            return '(%s)' % r
        return r

    def tostr(self, level=0):
        return self.seqtostr(', ', self.get_precedence(), level)

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        if isinstance(self.coeff, Symbolic.Number) \
           and isinstance(other.coeff, Symbolic.Number):
            c = abs(self.coeff).compare(abs(other.coeff))
        else:
            c = self.coeff.compare(other.coeff)
        if c: return c
        c = cmp(len(self.seq), len(other.seq))
        if c: return c
        for i1,i2 in zip(self.seq, other.seq):
            c = i1.compare(i2)
            if c: return c
        return 0

#
# End of SymbolicSequence class
#
################################################################################

class CommutativeSequence(SymbolicSequence):

    """ Base class for Add, Mul, And, Or classes.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls,*seq,**kws):
        """
        Seq() -> identity
        Seq(x) -> x
        Seq(2,3) -> 2 op 3
        Seq(x,2,3) -> Seq(2 op 3,x)
        Seq(x,y) -> Seq(identity,x,y)
        """
        if len(seq)==0: return Symbolic(cls.identity)
        seq = map(Symbolic,seq)
        if len(seq)==1: return seq[0]
        coeff, seq = cls.flatten_sequence(seq)
        if len(seq)==0: return coeff
        if len(seq)==1 and coeff==cls.identity:
            return seq[0]
        seq.sort(Symbolic.compare)
        return Symbolic.__new__(cls, coeff, seq)

    def astuple(self):
        if self.coeff==self.__class__.identity:
            return (self.__class__.__name__,)+self.seq
        return (self.__class__.__name__, self.coeff)+self.seq

    ############################################################################
    #
    # Substitution methods
    #

    def calc_substitute(self, subst, replacement):
        """
        (a op b).subst(a, c) -> b op c
        (a op b op c).subst(a op c, d) -> b op d
        """
        if subst.free_symbols().issubset(self.free_symbols()):
            if isinstance(subst, self.__class__):
                for s in subst.seq:
                    if not s.is_in(self.seq):
                        return self
                new_seq = [s for s in self.seq if not s.is_in(subst.seq)] + [replacement]
                if subst.coeff != self.__class__.identity:
                    new_seq.append(subst.coeff.neg_invert())
                return self.__class__(self.coeff, *new_seq)
            if subst.is_in(self.seq):
                i = subst.index_in(self.seq)
                new_seq = self.seq[:i] + (replacement,) + self.seq[i+1:]
                return self.__class__(self.coeff, *new_seq)
        flag, new_seq = self._apply_mth('substitute', self.astuple()[1:], (subst, replacement))
        if flag:
            return self.__class__(*new_seq)
        return self

#
# End of CommutativeSequence class
#
################################################################################

class NonCommutativeSequence(SymbolicSequence):
    """ Base class for NcMul
    """

    ###########################################################################
    #
    # Constructor methods
    #
    
    def __new__(cls,*seq):
        """
        Seq() -> identity
        Seq(x) -> x
        Seq(2,3) -> 2 op 3
        """
        if len(seq)==0: return Symbolic.Number(cls.identity)
        seq = map(Symbolic,seq)
        if len(seq)==1: return seq[0]
        coeff, seq = cls.flatten_sequence(seq)
        if len(seq)==0: return coeff
        if len(seq)==1 and coeff==cls.identity: return seq[0]
        return Symbolic.__new__(cls, coeff, seq)

#
# End of NonCommutativeSequence class
#
################################################################################

class Range(SymbolicSequence):
    """
    Range(x) -> x
    Range(x, a, b, [s])
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls,*seq):
        if len(seq) not in [1,3,4]:
            raise TypeError,'Range() takes 1 or 3 or 4 arguments (%s given)' % (len(seq))
        seq = map(Symbolic,seq)
        if len(seq)==1: return seq[0]
        if not isinstance(seq[0], Symbolic.Symbol):
            raise TypeError,'Range() 1st argument must be Symbol object but got %s object' \
                  % (seq[0].__class__.__name__)
        symbols = set()
        [symbols.update(s.symbols()) for s in seq[1:]]
        if seq[0] in symbols:
            raise ValueError,'Range() boundary contains variable symbol'
        obj = Symbolic.__new__(cls, seq[0], seq[1:])
        return obj

    ############################################################################
    #
    # Informational methods
    #

    def calc_free_symbols(self):
        r = set()
        for s in self.astuple()[2:]:
            r.update(s.free_symbols())
        return r        

    ###########################################################################
    #
    # Transformation methods
    #

    def calc_expanded(self):
        return Range(*[s.expand() for s in self.astuple()[1:]])

    def tostr(self, level=0):
        precedence = self.get_precedence()
        r = '%s = (%s)' % (self.coeff.tostr(), ', '.join([s.tostr() for s in self.seq]))
        if precedence <= level:
            return '(%s)' % r
        return r

#
# End of Range class
#
################################################################################


Symbolic.Constant = Constant
Symbolic.Range = Range

import parser

#EOF
