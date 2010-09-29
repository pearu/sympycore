# Author: Pearu Peterson
# Created: March 2008

from ..utils import MATRIX, MATRIX_DICT, MATRIX_DICT_T
from ..arithmetic.numbers import div
from .algebra import MatrixDict, Matrix

from ..core import init_module
init_module.import_lowlevel_operations()

def MATRIX_DICT_gauss_jordan_elimination(self, overwrite=False):
    """ Perform Gauss-Jordan elimination of a m x n matrix A.

    Outputs::

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
        B = MatrixDict(MATRIX(k, n, MATRIX_DICT), udata)
        gauss_jordan_elimination_MATRIX_T(m, n, udata)
    elif head.is_diagonal:
        raise NotImplementedError(`head, head.is_diagonal`)
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
    elif head.is_diagonal:
        raise NotImplementedError(`head`)
    else:
        U = MatrixDict(MATRIX(k, n, MATRIX_DICT), udata)
        pivot_table = lu_MATRIX(m, n, k, ldata, udata)
    P = Matrix(pivot_table, permutation=True).T
    return P, L, U

def gauss_jordan_elimination_MATRIX(m, n, data):
    data_get = data.get
    data_has = data.has_key
    rows = get_rc_map(data)
    for i in xrange(m):
        if 0:
            # for upper diagonal sparse matrix this is a bit slower..
            ncols, j = n, None
            for j1 in range(i,m):
                if data_has((j1,i)):
                    l = len(rows[j1])
                    if l <= ncols:
                        ncols, j = l, j1
            if j is None:
                continue
            a_ii = data[j,i]
            if i!=j:
                swap_rows_MATRIX(data, i, j, rows)
                swap_rc_map(rows, i, j)
        else:
            a_ii = data_get((i,i))
            if a_ii is None:
                for j in xrange(i+1, m):
                    a_ii = data_get((j,i))
                    if a_ii is not None:
                        break
                if a_ii is None:
                    continue
                swap_rows_MATRIX(data, i, j, rows)
                swap_rc_map(rows, i, j)
        irow = rows[i]
        for j in range(m):
            if j==i:
                continue
            u_ji = data_get((j,i))
            if u_ji is None:
                continue
            c = div(u_ji, a_ii)
            jrow = rows[j]
            jrow_add = jrow.add
            jrow_remove = jrow.remove
            for p in irow:
                if p < i: continue
                u_ip_c = data[i,p] * c
                jp = j,p
                b = data_get(jp)
                if b is None:
                    data[jp] = -u_ip_c
                    jrow_add(p)
                else:
                    if u_ip_c==b:
                        del data[jp]
                        jrow_remove(p)
                    else:
                        data[jp] = b - u_ip_c
            if not jrow:
                del rows[j]
        data[i,i] = 1
        
        for p in irow:
            if p <= i: continue
            ip = i,p
            data[ip] = div(data[ip], a_ii)

def gauss_jordan_elimination_MATRIX_T(m, n, data):
    data_get = data.get
    rows = get_rc_map_T(data)
    for i in xrange(m):
        a_ii = data_get((i,i))
        if a_ii is None:
            for j in xrange(i+1, m):
                a_ii = data_get((i,j))
                if a_ii is not None:
                    break
            if a_ii is None:
                continue
            swap_rows_MATRIX_T(data, i, j, rows)
            swap_rc_map(rows, i, j)
        irow = rows[i]
        for j in range(m):
            if j==i:
                continue
            u_ji = data_get((i,j))
            if u_ji is None:
                continue
            c = div(u_ji, a_ii)
            jrow = rows[j]
            for p in range(i,n):
                u_ip = data_get((p,i))
                if u_ip is None:
                    continue
                jp = p,j
                b = data_get(jp)
                if b is None:
                    data[jp] = -u_ip*c
                    jrow.add(p)
                else:
                    b -= u_ip*c
                    if b:
                        data[jp] = b
                    else:
                        del data[jp]
                        jrow.remove(p)
            if not jrow:
                del rows[j]
        data[i,i] = 1
        for p in range(i+1, n):
            ip = p,i
            data[ip] = div(data[ip], a_ii)

def get_rc_map(data):
    rows = {}
    for i, j in data:
        s = rows.get (i)
        if s is None:
            s = rows[i] = set ()
        s.add(j)
    return rows

def get_rc_map_T(data):
    rows = {}
    for j, i in data:
        s = rows.get (i)
        if s is None:
            s = rows[i] = set ()
        s.add(j)
    return rows

def swap_rc_map(rows, i, j):
    ri = rows.get(i)
    rj = rows.get(j)
    if rj is not None: del rows[j]
    if ri is not None: del rows[i]
    if rj is not None:
        rows[i] = rj
    if ri is not None:
        rows[j] = ri

def lu_MATRIX(m, n, k, ldata, udata):
    if m>n:
        for i in xrange(n,m):
            udata[(i,i)] = 1
    pivot_table = range(m)
    udata_get = udata.get
    udata_has = udata.has_key

    urows = get_rc_map(udata)
    lrows = get_rc_map(ldata)
    for i in xrange(m-1):
        ncols, j = n, None
        for j1 in range(i,m):
            if udata_has((j1,i)):
                l = len(urows[j1])
                if l <= ncols:
                    ncols, j = l, j1
        if j is None:
            continue
        a_ii = udata[j,i]
        if i!=j:
            pivot_table[i], pivot_table[j] = pivot_table[j], pivot_table[i]
            swap_rows_MATRIX(udata, i, j, urows)
            swap_rows_MATRIX(ldata, i, j, lrows)
            swap_rc_map(urows, i, j)
            swap_rc_map(lrows, i, j)
        irow = urows[i]
        for j in range (i+1,m):
            u_ji = udata_get((j,i))
            if u_ji is None:
                continue
            c = div(u_ji, a_ii)
            jrow = urows[j]
            jrow_add = jrow.add
            jrow_remove = jrow.remove
            for p in irow:
                if p < i: continue
                u_ip_c = udata[i,p] * c
                jp = j,p
                b = udata_get(jp)
                if b is None:
                    udata[jp] = -u_ip_c
                    jrow_add(p)
                else:
                    if b==u_ip_c:
                        del udata[jp]
                        jrow_remove(p)
                    else:
                        udata[jp] = b - u_ip_c
            if not jrow:
                del urows[j]
            if i<k and j<m:
                ldata[j, i] = c
                s = lrows.get(j)
                if s is None:
                    s = lrows[j] = set()
                s.add(i)
    for i in xrange(min(m, k)):
        ldata[i,i] = 1
    if m>n:
        crop_MATRIX(k, n, udata)
    return pivot_table

def lu_MATRIX_T(m, n, k, ldata, udata):
    if m>n:
        for i in xrange(n,m):
            udata[(i,i)] = 1    
    pivot_table = range(m)
    udata_get = udata.get
    udata_has = udata.has_key
    urows = get_rc_map_T(udata)
    lrows = get_rc_map(ldata)
    for i in xrange(m-1):
        ncols, j = n, None
        for j1 in range(i, m):
            if udata_has((i,j1)):
                l = len(urows[j1])
                if l <= ncols:
                    ncols, j = l, j1
        if j is None:
            continue
        a_ii = udata[i,j]
        if i!=j:
            pivot_table[i], pivot_table[j] = pivot_table[j], pivot_table[i]
            swap_rows_MATRIX_T(udata, i, j, urows)
            swap_rows_MATRIX(ldata, i, j, lrows)
            swap_rc_map(urows, i, j)
            swap_rc_map(lrows, i, j)
        irow = urows[i]
        for j in xrange(i+1,m):
            u_ji = udata_get((i,j))
            if u_ji is None:
                continue
            c = div(u_ji, a_ii)
            jrow = urows[j]
            jrow_add = jrow.add
            jrow_remove = jrow.remove
            for p in irow:
                if p < i: continue
                u_ip_c = udata[p,i] * c
                jp = p,j
                b = udata_get(jp)
                if b is None:
                    udata[jp] = -u_ip_c
                    jrow_add(p)
                else:
                    if b==u_ip_c:
                        del udata[jp]
                        jrow_remove(p)
                    else:
                        udata[jp] = b - u_ip_c
            if not jrow:
                del urows[j]
            if i<k and j<m:
                ldata[j, i] = c
                s = lrows.get(j)
                if s is None:
                    s = lrows[j] = set()
                s.add(i)
    for i in xrange(min(m, k)):
        ldata[i,i] = 1
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
    elif head.is_diagonal:
        raise NotImplementedError(`head`)
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

def swap_rows_MATRIX(data, i, j, rows=None):
    if i==j:
        return
    if rows is not None:
        d = {}
        data_pop = data.pop
        for k in rows.get(i,[]):
            d[j,k] = data_pop((i,k))
        for k in rows.get(j,[]):
            d[i,k] = data_pop((j,k))
        data.update(d)
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

def swap_cols_MATRIX(data, i, j, cols=None):
    if i==j:
        return
    if cols is not None:
        d = {}
        data_pop = data.pop
        for k in cols.get(i,[]):
            d[k,j] = data_pop((k,i))
        for k in cols.get(j,[]):
            d[k,i] = data_pop((k,j))
        data.update(d)
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
    elif head.is_diagonal:
        raise NotImplementedError(`head`)
    else:
        swap_rows_MATRIX(data, i, j)

def MATRIX_DICT_swap_cols(self, i, j):
    if not self.is_writable:
        raise TypeError('Cannot swap columns of a read-only matrix')
    head, data = self.pair
    if head.is_transpose:
        swap_cols_MATRIX_T(data, i, j)
    elif head.is_diagonal:
        raise NotImplementedError(`head`)
    else:
        swap_cols_MATRIX(data, i, j)

def MATRIX_DICT_trace(self):
    """ Return trace of a matrix.
    """
    head, data = self.pair
    m, n = head.shape
    s = 0
    if head.is_diagonal:
        dget = data.get
        for i in xrange(min(n,m)):
            s += dget((i, i), 0)
        return s
    if m != n:
        raise ValueError("matrix trace is only defined for square matrices but got %sx%s" % (m,n))
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
