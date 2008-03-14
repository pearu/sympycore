"""Provides various implementation specific constants.
"""

__docformat__ = 'restructuredtext'

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
POLY = intern('P')
DENSE_POLY = intern('DP')
MATRIX = intern('M')
DENSE_MATRIX = intern('DM')

head_to_string = {\
    OR:'OR', AND:'AND', NOT:'NOT',
    LT:'LT', LE:'LE', GT:'GT', GE:'GE', NE:'NE',
    BAND:'BAND', BOR:'BOR', BXOR:'BXOR', INVERT:'INVERT',
    POS:'POS', NEG:'NEG', ADD:'ADD', SUB:'SUB', MOD:'MOD', MUL:'MUL', DIV:'DIV', POW:'POW',
    NUMBER:'NUMBER', SYMBOL:'SYMBOL', APPLY:'APPLY', TUPLE:'TUPLE', LAMBDA:'LAMBDA',
    POLY:'POLY', DENSE_POLY:'DENSE_POLY', MATRIX:'MATRIX', DENSE_MATRIX:'DENSE_MATRIX'
    }

def get_head(head):
    """ Return head from head copy.

    Used by unpickler to ensure that objects head's can be compared
    using ``is``.
    """
    n = head_to_string.get(head, None)
    if n is None:
        return head
    return globals().get(n, head)
