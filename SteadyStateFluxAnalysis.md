# Introduction #

The sympycore.physics.sysbio package provides
a Python class `SteadyFluxAnalyzer` that is used
to define and analyse the steady state problem
of genome-scale metabolic networks.

The `SteadyFluxAnalyzer` class supports:

  * Reading metabolic network information from SBML files.
  * Parsing text strings for metabolic network information.
  * Solving the steady state problem using the GJE and SVD algorithms.
  * Comparing the results of steady state problem solvers.
  * Measuring CPU and memory usage of the steady state problem solvers.

This wiki page complements the [paper](http://www.biomedcentral.com/1752-0509/5/81/abstract)
```
  "Symbolic flux analysis for genome-scale metabolic networks"
  by David W. Schryer, Marko Vendelin, and Pearu Peterson.
  BMC Systems Biology 2011, 5:81.
  doi:10.1186/1752-0509-5-81.
```

# Requirements #

In addition to sympycore, one needs to install [lxml](http://lxml.de/installation.html#installation) for reading SBML files
and [numpy](http://sourceforge.net/projects/numpy/files/NumPy/) for using SVD algorithm. For installing sympycore, it is best to grab its sources from
[SVN](http://code.google.com/p/sympycore/source/checkout) and install it (see [Usage](http://code.google.com/p/sympycore/) for instructions).


# Example #

## Creating metabolic network instance ##

To use `SteadyFluxAnalyzer` for analysing metabolic networks, it has to be imported to Python:
```
>>> from sympycore.physics.sysbio import SteadyFluxAnalyzer
```
For a full documentation of this class, execute
```
>>> help(SteadyFluxAnalyzer)
```

The `SteadyFluxAnalyzer` constructor supports reading network information from both a Python string and a SBML file. In the following we demonstrate both ways.

For an example metabolic network we will use the system from slides [Genome-scale Metabolic Network Reconstruction](http://www.docstoc.com/docs/516768/Genome-scale-Metabolic-Network-Reconstruction), page 5.
This network can be read in from a string:
```
>>> example_network = '''
A => B
B => C
B <=> D
C => D
C => E
D => E
A <= 
C => 
D => 
E => 
'''
>>> ex = SteadyFluxAnalyzer (example_network, split_bidirectional_fluxes = True)
```
Note that when reaction string has empty side (as the last four right hand sides above) then
the corresponding line defines a transport flux. We specified `split_bidirectional_fluxes=True` so that the bidirectional reaction `B<=>D` will
have two columns in the stoichiometry matrix.

## Viewing stoichiometry ##

To see the stoichiometry matrix of the system, execute
```
>>> print ex
    R_A_B  R_B_C  R_B_D  R_D_B  R_C_D  R_C_E  R_D_E  R_A  R_C  R_D  R_E
 A     -1      0      0      0      0      0      0    1    0    0    0
 B      1     -1     -1      1      0      0      0    0    0    0    0
 C      0      1      0      0     -1     -1      0    0   -1    0    0
 D      0      0      1     -1      1      0     -1    0    0   -1    0
 E      0      0      0      0      0      1      1    0    0    0   -1
```
Here columns are labelled with reaction (flux) names and rows are labelled with metabolite names. The full lists of reaction and metabolite names are also available:
```
>>> print ex.reactions
['R_A_B', 'R_B_C', 'R_B_D', 'R_D_B', 'R_C_D', 'R_C_E', 'R_D_E', 'R_A', 'R_C', 'R_D', 'R_E']
>>> print ex.species
['A', 'B', 'C', 'D', 'E']
```

## Computing GJE kernel ##

We can compute the kernel of this stoichiometry matrix with the GJE algorithm:
```
>>> ex.compute_kernel_GJE ()
```
For large metabolic networks this can take a while. The computational time
scales as `N**2.5` where N is the number of reactions.

The kernel can be requested via get\_kernel\_GJE method that returns lists of fluxes and a kernel matrix:
```
>>> fluxes, indep_fluxes, kernel = ex.get_kernel_GJE ()
>>> print fluxes
['R_D', 'R_C', 'R_A_B', 'R_A', 'R_E', 'R_B_C', 'R_B_D', 'R_D_B', 'R_C_D', 'R_C_E', 'R_D_E']
```
Note that the order of flux names may be different from the order in `ex.reactions`. This new order defines the meaning of kernel rows and columns.
To be specific, by default, the first `R` fluxes are dependent fluxes
and the rest of `N-R` fluxes are independent fluxes.
Here `R` denotes the rank of the stoichiometric matrix:
```
>>> print ex.rank
5
```

To view the kernel matrix, use
```
>>> print ex.label_matrix (kernel, fluxes, indep_fluxes)
        R_B_C  R_B_D  R_D_B  R_C_D  R_C_E  R_D_E
   R_D      0      1     -1      1      0     -1
   R_C      1      0      0     -1     -1      0
 R_A_B      1      1     -1      0      0      0
   R_A      1      1     -1      0      0      0
   R_E      0      0      0      0      1      1
 R_B_C      1      0      0      0      0      0
 R_B_D      0      1      0      0      0      0
 R_D_B      0      0      1      0      0      0
 R_C_D      0      0      0      1      0      0
 R_C_E      0      0      0      0      1      0
 R_D_E      0      0      0      0      0      1
```
that can be interpreted as follows. Each flux (labelling a row) is equal
to a weighted sum of fluxes (labelling columns) where the weights are defined by the corresponding rows.
For instance, `R_A_B = R_B_C + R_B_D - R_D_B`.

## Choosing a different coordinate system ##

In the above computation the algorithm automatically chose which variables are independent and which are dependent. The choice was made to minimise the number of row operations. However, one may wish to get another set of independent variables. For example, transport fluxes are often more useful to be chosen as independent variables because their values can be measured. Such a selection can be accomplished by specifying which columns ought to be skipped from the GJE process, or inversely, which fluxes should be dependent fluxes. In our case, we can specify the list of dependent fluxes by counting the underscores in their names:
```
>>> dependent_candidates=[r for r in ex.reactions if r.count ('_')>1]
>>> print dependent_candidates
['R_A_B', 'R_B_C', 'R_B_D', 'R_D_B', 'R_C_D', 'R_C_E', 'R_D_E']
```
and then recomputing the GJE kernel gives:
```
>>> ex.compute_kernel_GJE(dependent_candidates=dependent_candidates)
>>> fluxes, indep_fluxes, kernel = ex.get_kernel_GJE()
>>> print ex.label_matrix (kernel, fluxes, indep_fluxes)
        R_B_D  R_D_B  R_D_E  R_A  R_D  R_E
 R_C_D     -1      1      1    0    1    0
 R_B_C     -1      1      0    1    0    0
   R_C      0      0      0    1   -1   -1
 R_C_E      0      0     -1    0    0    1
 R_A_B      0      0      0    1    0    0
 R_B_D      1      0      0    0    0    0
 R_D_B      0      1      0    0    0    0
 R_D_E      0      0      1    0    0    0
   R_A      0      0      0    1    0    0
   R_D      0      0      0    0    1    0
   R_E      0      0      0    0    0    1
```
Note that the all transport fluxes and few internal fluxes form a set of independent fluxes. And we have `R_A_B = R_A`.

To obtain the same kernel as given in [Genome-scale Metabolic Network Reconstruction](http://www.docstoc.com/docs/516768/Genome-scale-Metabolic-Network-Reconstruction),
one must use `dependent_candidates = ['R_A_B', 'R_B_C', 'R_B_D','R_C_E', 'R_A']`.
Note that the order of columns will be different from the reference, though.

## Viewing flux relations ##

To view the flux relations, one can use the following code:
```
>>> dep_fluxes = fluxes[:ex.rank]
>>> indep_symbols = map(Symbol,indep_fluxes)
>>> for i in range(ex.rank): print dep_fluxes[i],'=',[indep_symbols] * kernel[i].T
R_C_D =  R_D_B + R_D - R_B_D + R_D_E
R_B_C =  R_D_B - R_B_D + R_A
R_C =  R_A - R_D - R_E
R_C_E =  R_E - R_D_E
R_A_B =  R_A
```
Note that one of the transport fluxes, `R_C`, is in the list of dependent variables. This is because without this, the GJE algorithm
cannot complete the row reduction and so the routine automatically extends the given list of `dependent_candidates`.

## Checking correctness ##

To check that the GJE kernel is correct, that is, the solution
that it defines, satisfies the equation `stoichiometry * (kernel*indep_vars) = 0`.
Clearly, it is sufficient to verify that `stoichiometry * kernel` gives a null matrix.
To perform the multiplication, we have to be sure that the column labels (all fluxes) of stoichiometry matrix are exactly the same as the row labels of the kernel
matrix. For that, use the following code:
```
>>> fluxes, indep_fluxes, kernel = ex.get_kernel_GJE(ex.reactions)
>>> print ex.label_matrix (kernel, fluxes, indep_fluxes)
        R_B_D  R_D_B  R_D_E  R_A  R_D  R_E
 R_A_B      0      0      0    1    0    0
 R_B_C     -1      1      0    1    0    0
 R_B_D      1      0      0    0    0    0
 R_D_B      0      1      0    0    0    0
 R_C_D     -1      1      1    0    1    0
 R_C_E      0      0     -1    0    0    1
 R_D_E      0      0      1    0    0    0
   R_A      0      0      0    1    0    0
   R_C      0      0      0    1   -1   -1
   R_D      0      0      0    0    1    0
   R_E      0      0      0    0    0    1
```
where the argument to `ex.get_kernel_GJE` defines the order of
returned fluxes and hence also the order of kernel rows.
And now, from
```
>>> print ex.stoichiometry * kernel
 0  0  0  0  0  0
 0  0  0  0  0  0
 0  0  0  0  0  0
 0  0  0  0  0  0
 0  0  0  0  0  0
```
we see that the `kernel` matrix indeed defines the kernel of the stoichiometry matrix.

## Computing SVD kernel ##

We can compute the kernel of this stoichiometry matrix with the SVD algorithm:
```
>>> ex.compute_kernel_SVD()
>>> fluxes, kernel_SVD = ex.get_kernel_SVD()
```
where `kernel_SVD` is a numpy ndarray object and `fluxes` is a list of flux names. By definition, we have `fluxes = kernel_SVD * alpha` where `alpha` defines a column vector of parameters.

To view the kernel, one can use the following code
```
>>> alpha = ['a%s'%i for i in range(kernel_SVD.shape[1])]
>>> print ex.label_matrix(Matrix(kernel_SVD.round(decimals=3)), fluxes, alpha)
            a0      a1     a2      a3      a4      a5
 R_C_D   0.122    0.39  0.179  -0.389  -0.121  -0.511
 R_B_C   0.381  -0.074  0.433   0.101  -0.354   -0.28
   R_C  -0.245    -0.1  0.194   0.637  -0.217  -0.118
 R_C_E   0.505  -0.364  0.059  -0.146  -0.015   0.349
 R_A_B       0   0.059   0.54   0.133   0.192   0.133
 R_B_D  -0.594  -0.255  0.255  -0.331   0.008   0.263
 R_D_B  -0.212  -0.388  0.147  -0.362  -0.538   -0.15
 R_D_E  -0.255   0.629  0.076  -0.071  -0.187   0.184
   R_A       0   0.059   0.54   0.133   0.192   0.133
   R_D  -0.005  -0.106  0.211  -0.287   0.611  -0.283
   R_E    0.25   0.265  0.135  -0.217  -0.202   0.533
```
Note that the columns of the SVD kernel are orthonormal.

## Viewing statistics ##

Finally, to view the statistics of kernel computations, execute
```
>>> ex.show_statistics ()
system size:  (5, 11)
rank: 5
compute_kernel_GJE consumed 1848 bytes of memory
compute_kernel_GJE took 0.000115871429443 seconds
compute_kernel_GJE_parameters consumed 592 bytes of memory
compute_kernel_SVD consumed 1588 bytes of memory
compute_kernel_SVD took 0.000151872634888 seconds
get_kernel_GJE took 0.000129222869873 seconds
get_kernel_SVD took 2.59876251221e-05 seconds
get_sorted_reactions took 3.09944152832e-05 seconds
source consumed 19400 bytes of memory
variables consumed 784 bytes of memory
compute_kernel_GJE performed 7 row operations
```
that summaries the measured timings and memory consumptions of various methods.
The most interesting lines start with `compute_kernel_GJE`.

# Example of a large metabolic network #

## Reading SBML metabolic network models ##

The `SteadyFluxAnalyzer` class supports reading SMBL files, both from a local
hard disk as well as from Internet:
```
>>> ex = SteadyFluxAnalyzer ('http://www.biomedcentral.com/content/supplementary/1752-0509-4-160-s2.xml',
                              add_boundary_fluxes = True)
```
Here we used `add_boundary_fluxes=True` to have the system in open form by adding transport fluxes to all metabolites that take part of exactly one reaction. This is
a robust way to open the system when no additional knowledge about exchange
fluxes is available.

## Comparing GJE and SVD methods ##

The following statements compute both GJE and SVD kernels:
```
>>> ex.compute_kernel_GJE()
>>> ex.compute_kernel_SVD()
```
To compare the usage of computer resource of these methods, the result of
```
>>> ex.show_statistics()
system size:  (934, 1233)
rank: 924
compute_kernel_GJE consumed 1399272 bytes of memory
compute_kernel_GJE took 3.5154311657 seconds
compute_kernel_GJE_parameters consumed 176 bytes of memory
compute_kernel_SVD consumed 19149012 bytes of memory
compute_kernel_SVD took 3.21089506149 seconds
source consumed 3704568 bytes of memory
variables consumed 55712 bytes of memory
compute_kernel_GJE performed 8633 row operations
```
shows that both methods are almost equivalent with respect to
computational time, SVD being slight faster. However, The GJE
methods consumes considerable less computer memory.

To compare the results of GJE and SVD methods, execute
```
>>> print ex.get_relation_SVD_error ()
5.50701954797e-08
```
that shows the maximal relative flux error of the SVD result compared
to the GJE result. By the result of these methods we mean the
relation matrix that defines the relations between dependent and independent fluxes. See paper Methods for more information.