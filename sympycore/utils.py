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
        key = cls.__name__, args
        obj = cls._cache.get(key)
        if obj is None:
            obj = str.__new__(cls, '%s%s' % (cls.__name__, args))
            cls._cache[key] = obj
            obj.init(*args)
        return obj

    def init(self, *args):
        # derived class may set attributes here
        pass

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

OR = intern(' or ')
AND = intern(' and ')
NOT = intern('not ')

LT = intern('<')
LE = intern('<=')
GT = intern('>')
GE = intern('>=')
EQ = intern('==')
NE = intern('!=')

IN = intern(' in ')
NOTIN = intern(' not in ')

BAND = intern('&')
BOR = intern('|')
BXOR = intern('^')
INVERT = intern('~')

POS = intern('+')
NEG = intern('-')
TERMS = ADD = intern(' + ')
SUB = intern(' - ')
MOD = intern('%')
FACTORS = MUL = intern('*')
DIV = intern('/')
POW = intern('**')

NUMBER = intern('N')
SYMBOL = intern('S')
APPLY = intern('A')
TUPLE = intern('T')
LAMBDA = intern('L')

SUBSCRIPT = intern('[]')

POLY = intern('P')
DENSE_POLY = intern('DP')

DIFF = intern('D')

head_to_string = {\
    OR:'OR', AND:'AND', NOT:'NOT',
    LT:'LT', LE:'LE', GT:'GT', GE:'GE', NE:'NE', EQ:'EQ',
    IN:'IN', NOTIN:'NOTIN',
    BAND:'BAND', BOR:'BOR', BXOR:'BXOR', INVERT:'INVERT',
    POS:'POS', NEG:'NEG', ADD:'ADD', SUB:'SUB', MOD:'MOD', MUL:'MUL', DIV:'DIV', POW:'POW',
    NUMBER:'NUMBER', SYMBOL:'SYMBOL', APPLY:'APPLY', TUPLE:'TUPLE', LAMBDA:'LAMBDA',
    POLY:'POLY', DENSE_POLY:'DENSE_POLY',
    DIFF:'DIFF',
    }

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
            raise NotImplementedError(`storage`)

def get_head(head):
    """ Return head from head copy.

    Used by unpickler to ensure that objects head's can always be
    compared with ``is``.
    """
    n = head_to_string.get(head, None)
    if n is not None:
        return globals()[n]
    if isinstance(head, str):
        return eval(head, globals())
    return head


