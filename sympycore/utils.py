"""Provides various implementation specific constants (expression heads, etc).
"""

__docformat__ = 'restructuredtext'

import inspect

class HEAD(str):
    """ Base class to head constants.

    Head constants are singletons.
    """
    _cache = {}
    def __new__(cls, *args):
        key = '%s%s' % (cls.__name__, args)
        obj = cls._cache.get(key)
        if obj is None:
            obj = str.__new__(cls, key)
            cls._cache[key] = obj
            obj._key = key
            obj.init(*args)
        return obj

    def init(self, *args):
        # derived class may set attributes here
        pass #pragma NO COVER

    def as_unique_head(self):
        # used by the pickler support to make HEAD instances unique
        return self._cache[self._key]

class STDHEAD(HEAD):
    """ Standard head constants.

    STDHEAD(<repr-result>, <str-result>)
    """

    def init(self, op_repr, op_str = None, op_mth=None, op_rmth=None):
        if op_str is None:
            op_str = op_repr
        if op_mth is None:
            op_mth = '__'+op_repr.lower()+'__'
        if op_rmth is None:
            if op_mth.startswith('__'):
                op_rmth = '__r' + op_mth[2:]
        self.op_repr = op_repr
        self.op_str = op_str
        self.op_mth = op_mth
        self.op_rmth = op_rmth

    def __str__(self):
        return self.op_str

    def __repr__(self):
        return self.op_repr

# The following constants define both the order of operands
# as well as placing parenthesis for classes deriving from
# CollectingField:

str_SUM = -1
str_PRODUCT = -2
str_POWER = -3
str_APPLY = -4
str_SYMBOL = -5
str_NUMBER = -6

# The following constants are used by PrimitiveAlgebra and
# CollectingField classes.

OR = STDHEAD('OR', ' or ', '')
AND = STDHEAD('AND', ' and ', '')
NOT = STDHEAD('NOT', 'not ')

LT = STDHEAD('LT', '<')
LE = STDHEAD('LE', '<=')
GT = STDHEAD('GT', '>')
GE = STDHEAD('GE', '>=')
EQ = STDHEAD('EQ', '==')
NE = STDHEAD('NE', '!=')

IN = STDHEAD('IN', ' in ', '')
NOTIN = STDHEAD('NOTIN', ' not in ', '')

IS = STDHEAD('IS', ' is ', '')
ISNOT = STDHEAD('ISNOT', ' is not ', '')

BAND = STDHEAD('BAND', '&', '__and__')
BOR = STDHEAD('BOR', '|', '__or__')
BXOR = STDHEAD('BXOR', '^', '__xor__')
INVERT = STDHEAD('INVERT', '~')

POS = STDHEAD('POS', '+')
NEG = STDHEAD('NEG', '-')
TERMS = STDHEAD('TERMS', ' + ')
ADD = STDHEAD('ADD', ' + ')
SUB = STDHEAD('SUB', ' - ')
MOD = STDHEAD('MOD', '%')
MUL = STDHEAD('MUL', '*')
FACTORS = STDHEAD('FACTORS', '*')
DIV = STDHEAD('DIV', '/')
FLOORDIV = STDHEAD('FLOORDIV', '//')
POW = STDHEAD('POW', '**')
LSHIFT = STDHEAD('LSHIFT', '<<')
RSHIFT = STDHEAD('RSHIFT', '>>')
DIVMOD = STDHEAD('DIVMOD', 'divmod', '__divmod__', '')
SLICE = STDHEAD('SLICE', 'slice', '')

NUMBER = STDHEAD('NUMBER')
SYMBOL = STDHEAD('SYMBOL')
KWARG = STDHEAD('KWARG') # keyword argument
SPECIAL = STDHEAD('SPECIAL') # head for special data such as None, Ellipsis
APPLY = STDHEAD('APPLY')
TUPLE = STDHEAD('TUPLE', 'tuple', '')
LIST = STDHEAD('LIST', 'list', '')
DICT = STDHEAD('DICT', 'dict', '')
SET = STDHEAD('SET', 'set', '')
ATTR = STDHEAD('ATTR')
LAMBDA = STDHEAD('LAMBDA')

SUBSCRIPT = STDHEAD('SUBSCRIPT')

POLY = STDHEAD('POLY')
DENSE_POLY = STDHEAD('DENSE_POLY')

DIFF = STDHEAD('DIFF')

MATRIX_DICT = intern('MATRIX_DICT')
MATRIX_DICT_T = intern('MATRIX_DICT_T')
MATRIX_DICT_A = intern('MATRIX_DICT_A')
MATRIX_DICT_TA = intern('MATRIX_DICT_TA')
MATRIX_DICT_D = intern('MATRIX_DICT_D')
MATRIX_DICT_TD = intern('MATRIX_DICT_TD')

class MATRIX(HEAD):
    """ Matrix head singleton class.

    Usage::

      MATRIX(<rows>, <cols>, <storage>)

    where
    
      ``<rows>``     - number of matrix rows
      ``<cols>``     - number of matrix columns
      ``<strorage>`` - constant describing data storage properties:
                       MATRIX_DICT, MATRIX_DICT_T, MATRIX_DICT_A, MATRIX_DICT_TA,
                       MATRIX_DICT_D, MATRIX_DICT_DT
    """
    
    def init(self, rows, cols, storage):
        self.rows = rows
        self.cols = cols
        self.shape = (rows, cols)
        self.storage = storage

        self.is_transpose = is_transpose = storage in [MATRIX_DICT_T, MATRIX_DICT_TA, MATRIX_DICT_TD]
        self.is_array = storage in [MATRIX_DICT_A, MATRIX_DICT_TA]
        self.is_diagonal = storage in [MATRIX_DICT_D, MATRIX_DICT_TD]

        if storage==MATRIX_DICT:
            self.T = type(self)(cols, rows,  MATRIX_DICT_T)
            self.A = type(self)(rows, cols,  MATRIX_DICT_A)
            self.M = self
            self.D = type(self)(rows, cols,  MATRIX_DICT_D)
        elif storage==MATRIX_DICT_T:
            self.T = type(self)(cols, rows,  MATRIX_DICT)
            self.A = type(self)(rows, cols,  MATRIX_DICT_TA)
            self.M = self
            self.D = type(self)(rows, cols,  MATRIX_DICT_TD)
        elif storage==MATRIX_DICT_A:
            self.T = type(self)(cols, rows,  MATRIX_DICT_TA)
            self.A = self
            self.M = type(self)(rows, cols,  MATRIX_DICT)
            self.D = type(self)(rows, cols,  MATRIX_DICT_D)
        elif storage==MATRIX_DICT_TA:
            self.T = type(self)(cols, rows,  MATRIX_DICT_A)
            self.A = self
            self.M = type(self)(rows, cols,  MATRIX_DICT_T)
            self.D = type(self)(rows, cols,  MATRIX_DICT_TD)
        elif storage==MATRIX_DICT_D:
            self.T = type(self)(cols, rows,  MATRIX_DICT_T)
            self.A = type(self)(rows, cols,  MATRIX_DICT_A)
            self.M = type(self)(rows, cols,  MATRIX_DICT)
            self.D = self
        elif storage==MATRIX_DICT_TD:
            self.T = type(self)(cols, rows,  MATRIX_DICT)
            self.A = type(self)(rows, cols,  MATRIX_DICT_TA)
            self.M = type(self)(rows, cols,  MATRIX_DICT_T)
            self.D = self
        else:
            raise NotImplementedError(`storage`) #pragma NO COVER


