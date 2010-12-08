# Author: Pearu Peterson
# Created: March 2008

from ..utils import MATRIX, MATRIX_DICT, MATRIX_DICT_T
from ..arithmetic.numbers import div
from .algebra import MatrixDict, Matrix

from ..core import init_module
init_module.import_lowlevel_operations()

def MATRIX_DICT_gauss_jordan_elimination(self, swap_columns=False, overwrite=False, labels = None, return_pivot_info = False):
    """ Perform Gauss-Jordan elimination of a m x n matrix A.

    Parameters
    ----------

    swap_columns : bool

      When True then ensure that row echelon form has maximum number
      of nonzero diagonal elements by swapping columns.

    overwrite : bool
      When True then discard the content of matrix A.

    labels : {None,list}
      A list of column labels.

    return_pivot_info : bool
      When True, return pivot information, see below.

    Returns
    -------
    B : MatrixDict
      m1 x n matrix that is in row echelon form. m1 is the number of non-zero rows.

    pivot_table : list
      A n-list of column indices. pivot_table is returned only when
      swap_columns is True and labels is not specified.

    (dep, indep) : tuple
      A 2-tuple of column labels corresponding to dependent and
      independent variables. The 2-tuple is returned only when labels
      is specified.

    (row_pivot_table, column_pivot_table) : tuple
      A 2-tuple of lists corresponding to row and column pivot tables.
      The 2-tuple is returned only when return_pivot_info is True.
    """
    head, data = self.pair
    m, n = head.shape
    k = min(m,n)
    if overwrite and self.is_writable:
        udata = data
    else:
        udata = dict(data)
    if labels:
        swap_columns = True
    if head.is_transpose:
        m, row_pivot_table, pivot_table = gauss_jordan_elimination_MATRIX_T(m, n, udata, swap_columns = swap_columns)
        B = MatrixDict(MATRIX(m, n, MATRIX_DICT_T), udata)
    elif head.is_diagonal:
        raise NotImplementedError(`head, head.is_diagonal`)
    else:
        m, row_pivot_table, pivot_table = gauss_jordan_elimination_MATRIX(m, n, udata, swap_columns = swap_columns)
        B = MatrixDict(MATRIX(m, n, MATRIX_DICT), udata)
    if labels:
        dep = [labels[pivot_table[i]] for i in range (B.rows)]
        indep = [labels[pivot_table[i]] for i in range (B.rows, B.cols)]
        if return_pivot_info:
            return B, (dep, indep), (row_pivot_table, pivot_table)
        return B, (dep, indep)
    if swap_columns:
        if return_pivot_info:
            return B, (row_pivot_table, pivot_table)
        return B, pivot_table
    if return_pivot_info:
        return B, (row_pivot_table, pivot_table)
    return B

def MATRIX_DICT_lu(self, overwrite=False):
    """ Perform LU factorization of a m x n matrix A.

    Parameters
    ----------

      overwrite : bool
        When True then discard the content of matrix A.

    Returns
    -------

      P : MatrixDict
      L : MatrixDict
      U : MatrixDict
        LU decomposition matrices of A.

    Notes
    -----
        
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

def gauss_jordan_elimination_MATRIX(m, n, data, swap_columns = False):
    data_get = data.get
    data_has = data.has_key
    rows = get_rc_map(data)
    row_pivot_table = range(m)
    if swap_columns:
        pivot_table = range(n)
    else:
        pivot_table = None
    jpiv = 0    
    for i in xrange(m):
        ipiv = i

        while not data_has((ipiv, jpiv)):
            ipiv += 1
            if ipiv==m:
                ipiv = i
                jpiv += 1
                if jpiv==n:
                    break

        a_ii = data_get((ipiv, jpiv))
        if a_ii is None:
            break

        if swap_columns:
            if jpiv != i:
                swap_cols_MATRIX(data, jpiv, i)
                pivot_table[i], pivot_table[jpiv] = pivot_table[jpiv], pivot_table[i]
                rows = get_rc_map(data)
                jpiv = i

        if i!=ipiv:
            swap_rows_MATRIX(data, i, ipiv, rows)
            row_pivot_table[i], row_pivot_table[ipiv] = row_pivot_table[ipiv], row_pivot_table[i]
            swap_rc_map(rows, i, ipiv)
            ipiv = i
        irow = rows[i]
        for j in range(m):
            if j==i:
                continue
            u_ji = data_get((j,jpiv))
            if u_ji is None:
                continue
            c = div(u_ji, a_ii)
            jrow = rows[j]
            jrow_add = jrow.add
            jrow_remove = jrow.remove
            for p in irow:
                if p < jpiv: 
                    continue
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
        data[i,jpiv] = 1
        
        for p in irow:
            if p <= jpiv: 
                continue
            ip = i,p
            data[ip] = div(data[ip], a_ii)
    if rows:
        return max(rows)+1,row_pivot_table, pivot_table
    return 0, row_pivot_table, pivot_table

def gauss_jordan_elimination_MATRIX_T(m, n, data, swap_columns = False):
    data_get = data.get
    data_has = data.has_key
    rows = get_rc_map_T(data)
    row_pivot_table = range(m)
    if swap_columns:
        pivot_table = range(n)
    else:
        pivot_table = None
    jpiv = 0
    for i in xrange(m):
        ipiv = i

        while not data_has((jpiv, ipiv)):
            ipiv += 1
            if ipiv==m:
                ipiv = i
                jpiv += 1
                if jpiv==n:
                    break
        a_ii = data_get((jpiv, ipiv))
        if a_ii is None:
            break

        if swap_columns:
            if jpiv != i:
                swap_cols_MATRIX_T(data, jpiv, i)
                pivot_table[i], pivot_table[jpiv] = pivot_table[jpiv], pivot_table[i]
                rows = get_rc_map_T(data)
                jpiv = i

        if i!=ipiv:
            swap_rows_MATRIX_T(data, i, ipiv, rows)
            row_pivot_table[i], row_pivot_table[ipiv] = row_pivot_table[ipiv], row_pivot_table[i]
            swap_rc_map(rows, i, ipiv)
            ipiv = i
        irow = rows[i]
        for k in range(m):
            if k==ipiv:
                continue
            u_ji = data_get((jpiv,k))
            if u_ji is None:
                continue
            c = div(u_ji, a_ii)
            jrow = rows[k]
            jrow_add = jrow.add
            jrow_remove = jrow.remove
            for p in irow:
                if p < jpiv: 
                    continue
                u_ip_c = data[p,i] * c
                kp = p,k
                b = data_get(kp)
                if b is None:
                    data[kp] = -u_ip_c
                    jrow_add(p)
                else:
                    if u_ip_c==b:
                        del data[kp]
                        jrow_remove(p)
                    else:
                        data[kp] = b - u_ip_c
            if not jrow:
                del rows[k]
        data[jpiv,i] = 1
        
        for p in irow:
            if p <= jpiv: 
                continue
            ip = p,i
            data[ip] = div(data[ip], a_ii)

    if rows:
        return max(rows)+1, row_pivot_table, pivot_table
    return 0, row_pivot_table, pivot_table

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
