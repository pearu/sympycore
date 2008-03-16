
from ..utils import MATRIX, MATRIX_DICT
from ..arithmetic.numbers import div
from .algebra import MatrixDict, Matrix

def MATRIX_DICT_lu(self):
    """ Perform LU factorization of a m x n matrix A.

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

def lu_MATRIX(m, n, k, ldata, udata):
    if m>n:
        for i in xrange(n,m):
            udata[(i,i)] = 1
    pivot_table = range(m)
    udata_get = udata.get
    for i in xrange(m-1):
        a_ii = udata.get((i,i))
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
    """ Remove elements that are out of dimensions.
    """
    head, data = self.pair
    m, n = head.shape
    if head.is_transpose:
        crop_MATRIX_T(m, n, data)
    else:
        crop_MATRIX(m, n, data)

def crop_MATRIX(m, n, data):
    for (i,j) in data:
        if 0<=i<m and 0<=j<n:
            continue
        del data[i,j]

def crop_MATRIX_T(m, n, data):
    for (j, i) in data:
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
    head, data = self.pair
    if head.is_transpose:
        swap_rows_MATRIX_T(data, i, j)
    else:
        swap_rows_MATRIX(data, i, j)

def MATRIX_DICT_swap_cols(self, i, j):
    head, data = self.pair
    if head.is_transpose:
        swap_cols_MATRIX_T(data, i, j)
    else:
        swap_cols_MATRIX(data, i, j)
