# General notes #

sympycore matrix support should provide useful interfaces to
matrix algebra. Therefore, operations with matrices by default
assume matrix operations. E.g. `A*B` is matrix product, `exp(A)` is
matrix exponent, etc.

For symbolic array operations, use, for example, NumPy ndarray object.

# Constructing matrices #

```
Matrix(n)                   - n x n matrix of zeros [IMPLEMENTED]
Matrix(n, random=True)      - n x n matrix of random values in [-10,10] [IMPLEMENTED]
Matrix(n, random=[l, u])    - n x n matrix of random values in [l, u] [IMPLEMENTED]
Matrix(m, n)                - m x n matrix of zeros [IMPLEMENTED]
Matrix(m, n, random=True)   - n x m matrix of random values in [-10,10] [IMPLEMENTED]
Matrix(m, n, random=[l, u]) - n x m matrix of random values in [l, u] [IMPLEMENTED]
Matrix(seq)                 - n x 1 matrix where n = len(seq) [IMPLEMENTED]
Matrix(seq, permutation=True) - n x n permutation matrix where n = len(seq) [IMPLEMENTED]
Matrix(seq, diagonal=True)  - n x n diagonal matrix where n=len(seq) [IMPLEMENTED]
Matrix(array) - m x n matrix composed from array (can be a list of lists) [IMPLEMENTED]
Matrix(m, n, dict) - m x n matrix with nonzero elements defined by dict [IMPLEMENTED]
Matrix(m, n, seq)  - m x n matrix with rows in seq [IMPLEMENTED]

eye(m,n=m,k=0)     - m x n matrix with k-th diagonal containing 1-s [IMPLEMENTED]
concatenate(A, B, ...) - join matrices A, B, .. along rows [IMPLEMENTED]
concatenate(A, B, ..., axis=1) - join matrices A, B, .. along columns [IMPLEMENTED]
concatenate(A, B, ..., diagonal=True) - join matrices A, B, .. along diagonal [IMPLEMENTED]
```

Matrices are mutable until `.is_writable==True`.

# Accessing and modifying matrices #

```
A[i,j]       - element (i,j) of A [IMPLEMENTED]
A[i], A[i,:] - i-th row of A as a matrix [IMPLEMENTED]
A[:,j]       - j-th column of A as a matrix [IMPLEMENTED]
A[i:j]       - i to j-1 rows of A as a matrix [IMPLEMENTED]
A[:,i:j]     - i to j-1 columns of A as a matrix [IMPLEMENTED]
A[<slice>, <slice>] - submatrix of A as a matrix [IMPLEMENTED]
A.D[k] - k-th diagonal of A as a single column matrix [IMPLEMENTED]

A[i,j]=value              - set element (i,j) of A to value [IMPLEMENTED]
A[<slice>, <slice>]=value - set submatrix of A to value,
                            if value is matrix then it
                            must have proper size [IMPLEMENTED]
A.D[k]=value              - set k-th diagonal of A to value, 
                            k==0 refers to main diagonal, 
                            k<0 to lower diagonals [IMPLEMENTED]
                            value can be single column matrix [IMPLEMENTED]
A.swap_rows(i,j) - swap rows in place [IMPLEMENTED]
A.swap_cols(i,j) - swap columns in place [IMPLEMENTED]
A.crop()         - crop items that are out of matrix bounds, return matrix [IMPLEMENTED]
A.resize(m,n)    - return resized view of a matrix, don't copy data and don't crop [IMPLEMENTED]
```
All access methods copy data.

# Matrix operations #

If `A` and `B` are matrices then
```
A + B - matrix sum [IMPLEMENTED]
A + b - matrix-scalar sum [IMPLEMENTED]
A += v - inplace add [IMPLEMENTED]
A * B - matrix dot product [IMPLEMENTED]
A.A * B - elementwise product, result has the view of rhs [IMPLEMENTED]
A * B.A - elementwise product, result has the view of rhs, ie array view [IMPLEMENTED]
A * b - matrix-scalar product [IMPLEMENTED]
A *= v - inplace product [IMPLEMENTED]
a / B - scalar-inverse-matrix product [IMPLEMENTED]
A / b - matrix-scalar division [IMPLEMENTED]
A // b - solve system of equations A * x = b, if b is matrix then x will be also matrix [IMPLEMENTED]
A ** n - matrix power, n can be non-integer [IMPLEMENTED for integer n]
```

# Special properties #

If `A` is a matrix instance then
```
A.rows - number of A rows [IMPLEMENTED]
A.cols - number of A columns [IMPLEMENTED]
A.shape - (A.rows, A.cols) [IMPLEMENTED]
A.is_square - check if A is square [IMPLEMENTED]
A.is_lower - check if A is lower triangular matrix [IMPLEMENTED]
A.is_upper - check if A is upper triangular matrix [IMPLEMENTED]
A.is_orthogonal - check if the rows of A are orthogonal (A*A.T=identity) [IMPLEMENTED]
A.is_identity - check if A is identity matrix [IMPLEMENTED]
A.T - transpose view of matrxi A  [IMPLEMENTED]
A.I - inverse of A, cache the result [IMPLEMENTED]
A.V - return a vector instance of a one-column matrix A
A.A - return array (elementwise) view of matrix A [IMPLEMENTED]
A.M - return matrix view of matrix A (to reset elementwise view) [IMPLEMENTED]
A.D - return diagonal view of matrix A, eg A.D[0] is main diagonal as a 1-column matrix [IMPLEMENTED]
```
Views of matrices do not copy data.

# Linear Algebra #

```
A.trace() - trace of A. [IMPLEMENTED]
A.lu() - PLU factorization of A [IMPLEMENTED]
A.solve(b) - solve system of equations A*x=b [IMPLEMENTED]
A.qr() - QR factorization of A.
A.svd() - singular value decomposition of A
A.cholesky() - Cholesky decomposition of a matrix A
A.schur() - Schur decomposition of a matrix A
A.hessenberg() - Hessenberg form of a matrix A
A.inv() - inverse of square matrix A. [IMPLEMENTED]
A.det() - determinant of square matrix A. [IMPLEMENTED]
A.rank() - return rank (# of linearly independent rows) of a matrix A.
A.norm() - norm of a matrix A
A.eig() - eigenvectors and eigenvalues of a square matrix A.
A.lstsq() - solve least square problem
A.charpoly(x) - characteristic polynomial of A
```

# Matrix functions, calculus #

```
exp(A) - matrix exponential of A
exp(A.A) - elementwise exponent of A
log, sin, cos, tan, cot, sqrt, sign, <arbitrary function>
jacobian(expressions, var) - jacobian
hessian(expr, var) - hessian of expr
wronskian(expressions, var) - wronskian
```

# Open issues #

  1. Issue:
```
  A ?? B - element-wise product, division, power
  Solution:
  A.A * B - result has the view of lhs --- array view   [IMPLEMENTED]
  A * B.A - result has the view of lhs --- matrix view  [IMPLEMENTED]
  Same applies for division and power.
```

  1. Issue: `A.A` or `A.E`? Answer: `A.A` `[IMPLEMENTED]`

  1. Issue: should array operations have the view of rhs? Eg `A.A * B.M` has matrix view, `A * B.A` has array view. Answer: YES. `[IMPLEMENTED]`