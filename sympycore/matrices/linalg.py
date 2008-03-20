# Author: Pearu Peterson
# Created: March 2008

from ..utils import MATRIX, MATRIX_DICT
from ..arithmetic.numbers import div
from .algebra import MatrixDict, Matrix

def MATRIX_DICT_gauss_jordan_elimination(self, overwrite=False):
    """ Perform Gauss-Jordan elimination of a m x n matrix A.

    Outputs::

      P - m x m permutation matrix
      B - m x n matrix where the lhs part is unit matrix
    """
    head, data = self.pair
    m, n = head.shape
    k = min(m,n)
    if overwrite and self.is_writable:
        udata = data
    else:
        udata = dict(data)
    if head.is_transpose:
        raise NotImplementedError
        B = MatrixDict(MATRIX(k, n, MATRIX_DICT_T), udata)
        gauss_jordan_elimination_MATRIX_T(m, n, udata)
    else:
        B = MatrixDict(MATRIX(k, n, MATRIX_DICT), udata)
        gauss_jordan_elimination_MATRIX(m, n, udata)
    return B

def MATRIX_DICT_lu(self, overwrite=False):
    """ Perform LU factorization of a m x n matrix A.

    Parameters::

      overwrite=False - if True then discard the content of matrix A

    Outputs::
    
      P, L, U - LU decomposition matrices of A.

    Definitions::
        
      P - m x m permuation matrix
      L - m x k lower triangular or trapezoidal matrix with unit-diagonal
      U - k x n upper triangular or trapezoidal matrix
      k = min(m,n)
      
      A = P * L * U
    """
    head, data = self.pair
    m, n = head.shape
    k = min(m, n)
    ldata = {}
    if overwrite and self.is_writable:
        udata = data
    else:
        udata = dict(data)
    L = MatrixDict(MATRIX(m, k, MATRIX_DICT), ldata)
    if head.is_transpose:
        U = MatrixDict(MATRIX(k, n, MATRIX_DICT_T), udata)
        pivot_table = lu_MATRIX_T(m, n, k, ldata, udata)
    else:
        U = MatrixDict(MATRIX(k, n, MATRIX_DICT), udata)
        pivot_table = lu_MATRIX(m, n, k, ldata, udata)
    P = Matrix(pivot_table, permutation=True).T
    return P, L, U

def gauss_jordan_elimination_MATRIX(m, n, data):
    data_get = data.get
    for i in xrange(m):
        a_ii = data_get((i,i))
        if a_ii is None:
            for j in xrange(i+1, m):
                a_ii = data_get((j,i))
                if a_ii is not None:
                    break
            if a_ii is None:
                continue
            swap_rows_MATRIX(data, i, j)
        for j in range(m):
            if j==i:
                continue
            u_ji = data_get((j,i))
            if u_ji is None:
                continue
            c = div(u_ji, a_ii)
            for p in range(i,n):
                u_ip = data_get((i,p))
                if u_ip is None:
                    continue
                jp = j,p
                b = data_get(jp)
                if b is None:
                    data[jp] = -u_ip*c
                else:
                    b -= u_ip*c
                    if b:
                        data[jp] = b
                    else:
                        del data[jp]
        data[i,i] = 1
        for p in range(i+1, n):
            ip = i,p
            u_ip = data_get(ip)
            if u_ip is None:
                continue
            data[ip] = div(u_ip, a_ii)

def lu_MATRIX(m, n, k, ldata, udata):
    if m>n:
        for i in xrange(n,m):
            udata[(i,i)] = 1
    pivot_table = range(m)
    udata_get = udata.get
    for i in xrange(m-1):
        a_ii = udata_get((i,i))
        if a_ii is None:
            for j in xrange(i+1, m):
                a_ii = udata_get((j,i))
                if a_ii is not None:
                    break
            if a_ii is None:
                continue
            pivot_table[i], pivot_table[j] = pivot_table[j], pivot_table[i]
            swap_rows_MATRIX(udata, i, j)
            swap_rows_MATRIX(ldata, i, j)
        for j in xrange(i+1,m):
            u_ji = udata_get((j,i))
            if u_ji is None:
                continue
            c = div(u_ji, a_ii)
            for p in xrange(i,n):
                u_ip = udata_get((i,p))
                if u_ip is None:
                    continue
                jp = j,p
                b = udata_get(jp)
                if b is None:
                    udata[jp] = -u_ip*c
                else:
                    b -= u_ip*c
                    if b:
                        udata[jp] = b
                    else:
                        del udata[jp]
            if i<k and j<m and c:
                ldata[j, i] = c
        if i<k:
            ldata[i,i] = 1
        ldata[k-1, k-1] = 1
    if m>n:
        crop_MATRIX(k, n, udata)
    return pivot_table

def lu_MATRIX_T(m, n, k, ldata, udata):
    if m>n:
        for i in xrange(n,m):
            udata[(i,i)] = 1    
    pivot_table = range(m)
    udata_get = udata.get
    for i in xrange(m-1):
        a_ii = udata_get((i,i))
        if a_ii is None:
            for j in xrange(i+1, m):
                a_ii = udata_get((i,j))
                if a_ii is not None:
                    break
            if a_ii is None:
                continue
            pivot_table[i], pivot_table[j] = pivot_table[j], pivot_table[i]
            swap_rows_MATRIX_T(udata, i, j)
            swap_rows_MATRIX(ldata, i, j)
        for j in xrange(i+1,m):
            u_ji = udata_get((i,j))
            if u_ki is None:
                continue
            c = div(u_ji, a_ii)
            for p in xrange(i,n):
                u_ip = udata_get((p,i))
                if u_ip is None:
                    continue
                jp = p,j
                b = udata_get(jp)
                if b is None:
                    udata[jp] = -u_ip*c
                else:
                    b -= u_ip*c
                    if b:
                        udata[jp] = b
                    else:
                        del udata[jp]
            if i<k and j<m and c:
                ldata[j, i] = c
        if i<k:
            ldata[i,i] = 1
        ldata[k-1, k-1] = 1
    if m>n:
        crop_MATRIX_T(k, n, udata)
    return pivot_table

def MATRIX_DICT_crop(self):
    """ Remove matrix elements that are out of dimensions inplace and return the matrix.
    """
    if not self.is_writable:
        raise TypeError('Cannot crop read-only matrix inplace')
    head, data = self.pair
    m, n = head.shape
    if head.is_transpose:
        crop_MATRIX_T(m, n, data)
    else:
        crop_MATRIX(m, n, data)
    return self

def crop_MATRIX(m, n, data):
    for (i,j) in data.keys():
        if 0<=i<m and 0<=j<n:
            continue
        del data[i,j]

def crop_MATRIX_T(m, n, data):
    for (j, i) in data.keys():
        if 0<=i<m and 0<=j<n:
            continue
        del data[j, i]

def swap_rows_MATRIX(data, i, j):
    if i==j:
        return
    row_i = []
    row_j = []
    for index, element in data.items():
        i0 = index[0]
        if i0==i:
            row_i.append((index[1], element))
            del data[index]
        elif i0==j:
            row_j.append((index[1], element))
            del data[index]
    for k, element in row_i:
        data[j, k] = element
    for k, element in row_j:
        data[i, k] = element

def swap_cols_MATRIX(data, i, j):
    if i==j:
        return
    column_i = []
    column_j = []
    for index, element in data.items():
        i0 = index[1]
        if i0==i:
            column_i.append((index[0], element))
            del data[index]
        elif i0==j:
            column_j.append((index[0], element))
            del data[index]
    for k, element in column_i:
        data[k, j] = element
    for k,element in column_j:
        data[k, i] = element

swap_rows_MATRIX_T = swap_cols_MATRIX
swap_cols_MATRIX_T = swap_rows_MATRIX

def MATRIX_DICT_swap_rows(self, i, j):
    if not self.is_writable:
        raise TypeError('Cannot swap rows of a read-only matrix')
    head, data = self.pair
    if head.is_transpose:
        swap_rows_MATRIX_T(data, i, j)
    else:
        swap_rows_MATRIX(data, i, j)

def MATRIX_DICT_swap_cols(self, i, j):
    if not self.is_writable:
        raise TypeError('Cannot swap columns of a read-only matrix')
    head, data = self.pair
    if head.is_transpose:
        swap_cols_MATRIX_T(data, i, j)
    else:
        swap_cols_MATRIX(data, i, j)

def MATRIX_DICT_trace(self):
    head, data = self.pair
    m, n = head.shape
    s = 0
    if m != n:
        raise ValueError("matrix trace is only defined for square matrices")
    sparse = len(data) < m
    if sparse:
        for (i, j), element in data.items():
            if i == j:
                s += element
    else:
        dget = data.get
        for i in xrange(n):
            s += dget((i, i), 0)
    return s
