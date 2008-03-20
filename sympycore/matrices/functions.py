""" Provides Matrix support.
"""
#
# Author: Pearu Peterson
# Created: March 2008
#

__docformat__ = "restructuredtext"
__all__ = ['eye']

from ..utils import MATRIX, MATRIX_DICT
from .algebra import MatrixDict

def eye(m, n=None, k=0):
    """ Return n x m matrix where the k-th diagonal is all ones,
    everything else is zeros.
    """
    if n is None:
        n = m
    d = {}
    if k<0:
        for i in range(min(m,n)+k):
            d[i-k,i] = 1
    else:
        for i in range(min(m,n)-k):
            d[i,i+k] = 1
    return MatrixDict(MATRIX(m, n, MATRIX_DICT), d)
