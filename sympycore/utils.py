"""Provides various implementation specific constants (expression heads, etc).
"""

__docformat__ = 'restructuredtext'

import inspect

class HEAD(object):
    """ Base class to head constants.

    Head constants are singletons.
    """
    _cache = {}
    def __new__(cls, *args):
        key = '%s%s' % (cls.__name__, args)
        obj = cls._cache.get(key)
        if obj is None:
            obj = object.__new__(cls)
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

# The following constants define both the order of operands
# as well as placing parenthesis for classes deriving from
# CollectingField:

str_SUM = -1
str_PRODUCT = -2
str_POWER = -3
str_APPLY = -4
str_SYMBOL = -5
str_NUMBER = -6

# The following constants are used by Verbatim and
# CollectingField classes.

from heads import *

#POLY = HEAD('POLY')
#DENSE_POLY = HEAD('DENSE_POLY')

DIFF = HEAD('DIFF')

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


