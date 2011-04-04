

# Author: Pearu Peterson
# Created: April 2011

from __future__ import division

import os
import random
import time
from collections import defaultdict

from ...matrices import Matrix
from .io import load_stoic_from_sbml, load_stoic_from_text

class SteadyFluxAnalyzer(object):
    """ Base class for analyzing the steady state of a metabolic network.


    Attributes
    ----------
    species : list
      A list of species names or row names.
    reaction : list
      A list of reaction names or column names.
    stoichiometric : Matrix
      A stoichiometric matrix.

    """

    def __init__(self, source,
                 discard_boundary_species=False,
                 add_boundary_fluxes=False,
                 ):
        """
        Parameters
        ----------
        source : str
          A file name to sbml file or a string with reaction definitions.
          For internal processing source can also be tuple.

        discard_boundary_species : bool

          When True then discard species that are reactants or
          products of the full network. The corresponding
          stoichiometry system will be open. For example, in a
          reaction ``A -> B -> C`` the species A and C are reactant
          and product of the system and after discarding A and C, the
          system will be open: ``-> B ->`` .  In the case of a
          reaction `` -> A -> B + C`` the system will be made open by
          adding new reactions `` B-> `` and `` C -> ``.

        add_boundary_fluxes : bool

          When True then add boundary fluxes to boundary
          species.  The corresponding stoichiometry system will be
          open.  For example, in a reaction ``A -> B -> C`` the
          species A and C are reactant and product of the system and
          after introducing boundary fluxes, the system will be open:
          ``-> A -> B -> C ->``.  New flux names start with prefix
          ``BR_``.

        See also
        --------
        load_stoic_from_sbml, load_stoic_from_text, discard_boundary_species, add_boundary_fluxes
        """
        if isinstance (source, str):
            if os.path.isfile (source):
                stoic_dict, species, reactions, species_info, reactions_info = \
                    load_stoic_from_sbml(source)
            else:
                stoic_dict, species, reactions, species_info, reactions_info = \
                    load_stoic_from_text(source)
        elif isinstance (source, tuple):
            stoic_dict, species, reactions, species_info, reactions_info = source
        else:
            raise TypeError ('expected source to be str or tuple but got %r' % (type(source)))
        if discard_boundary_species:
            stoic_dict, species, reactions, species_info, reactions_info = \
                self.discard_boundary_species(stoic_dict, species, reactions, species_info, reactions_info)
        if add_boundary_fluxes:
            stoic_dict, species, reactions, species_info, reactions_info = \
                self.add_boundary_fluxes(stoic_dict, species, reactions, species_info, reactions_info)

        self.species = species
        self.species_info = species_info
        self.reactions = reactions
        self.reactions_info = reactions_info
        self.stoichiometric = Matrix(len (species), len (reactions), stoic_dict)
        self.kernel_GJE_data = None
        self.kernel_SVD_data = None

    def __repr__(self):
        return '%s((%r, %r, %r, %r, %r))' % (self.__class__.__name__,
                                             self.stoichiometric, self.species, self.reactions,
                                             self.species_info, self.reactions_info)

    def __str__(self, max_nrows=20, max_ncols=10):
        mat = self.label_matrix(self.stoichiometric, self.species, self.reactions)
        return mat.__str__(max_nrows=max_nrows, max_ncols=max_ncols)

    def label_matrix(self, matrix, row_labels, col_labels):
        """ Return a matrix with labeled rows and columns.
        """
        m, n = matrix.shape
        new_matrix = Matrix(m+1, n+1)
        new_matrix[1:, 1:] =  matrix
        for i, r in enumerate (col_labels):
            new_matrix[0,i+1] = r
        for i, r in enumerate (row_labels):
            new_matrix[i+1,0] = r
        new_matrix[0,0] = ' '
        return new_matrix

    @property
    def sparsity(self):
        m,n = self.stoichiometric.shape
        return len (self.stoichiometric.data)/(m*n)

    @property
    def rank (self):
        self.compute_kernel_GJE()        
        return len(self.dependent_variables)

    def get_splitted_reactions (self):
        """ Split reactions to a list of dependent and independent
        reactions.

        Returns
        -------
        leading_cols_canditates, trailing_cols_canditates : list
          Lists of integers.
        """
        reactions = self.reactions
        independent_cols = []
        for reaction_id in reactions:
            if reaction_id.startswith('BR_'):
                independent_cols.append(reactions.index(reaction_id))
        leading_cols_canditates = sorted(set(range(len(reactions))).difference(independent_cols))
        trailing_cols_canditates = independent_cols
        return leading_cols_canditates, trailing_cols_canditates

    def grow(self, factor=2, shuffle=True):
        """ Increase the size of network by a factor.

        Parameters
        ----------
        factor : int
          Specify the factor for the increase.
        shuffle : bool
          When True then shuffle the species and reactions lists of
          the new network.

        Returns
        -------
        network : SteadyFluxAnalyzer
        """
        m0, n0 = self.stoichiometric.shape
        m1, n1 = m0*factor, n0*factor
        species = []
        reactions = []
        for i in range (factor):
            for s in self.species:
                species.append('%s_%s' % (s, i))
            for s in self.reactions:
                reactions.append('%s_%s' % (s, i))
        rindices = range(m1)
        indices = range(n1)
        if shuffle:
            random.shuffle (rindices)
            random.shuffle (indices)
            species = [species[i] for i in rindices]
            reactions = [reactions[i] for i in indices]

        data = {}
        data0 = self.stoichiometric[:].data # copy when transposed
        for k in range (factor):
            for (i,j), v in data0.iteritems():
                data[rindices[i+ k*m0], indices[j+ k*n0]] = v 
        return SteadyFluxAnalyzer((data, species, reactions, {}, {}))

    def compute_kernel_GJE(self,
                           leading_row_selection='sparsest first',
                           leading_column_selection='sparsest first'):
        """ Compute the kernel of stoichiometric matrix via GJE routine.

        Parameters
        ----------
        leading_row_selection, leading_column_selection : str
          Specify parameters to get_gauss_jordan_elimination_operations method.

        See also
        --------
        MatrixBase.get_gauss_jordan_elimination_operations
        """
        #TODO: recompute data when parameters to get_gauss_jordan_elimination_operations are changed
        if self.kernel_GJE_data is None:
            leading_cols_canditates, trailing_cols_canditates = self.get_splitted_reactions()
            start = time.time ()
            gj, row_operations, leading_rows, leading_cols, zero_rows = \
                result = self.stoichiometric.get_gauss_jordan_elimination_operations(leading_cols=leading_cols_canditates,
                                                                                     trailing_cols = trailing_cols_canditates,
                                                                                     leading_row_selection=leading_row_selection,
                                                                                     leading_column_selection=leading_column_selection)
            end = time.time()
            self.kernel_GJE_data = result
            self.compute_kernel_GJE_elapsed = end - start

            independent_variables = []
            dependent_variables = []
            for k, variable in enumerate(self.reactions):
                if k in leading_cols:
                    dependent_variables.append(variable)
                else:
                    independent_variables.append(variable)
            self.dependent_variables = dependent_variables
            self.independent_variables = independent_variables

            self.kernel_GJE_data_parameters = leading_row_selection, leading_column_selection
        else:
            assert (self.kernel_GJE_data_parameters == (leading_row_selection, leading_column_selection))

    def get_sorted_reactions(self):
        from sympycore.matrices.linalg import  get_rc_map
        self.compute_kernel_GJE()
        start = time.time ()
        gj, row_operations, leading_rows, leading_cols, zero_rows = self.kernel_GJE_data
        l = []
        rows = get_rc_map(gj.data)
        for i0,j0 in zip (leading_rows, leading_cols):
            row = rows[i0]
            row.remove (j0)
            if row:
                l.append ((len(row),-min(row), self.reactions[j0]))
            else:
                l.append ((len(row),0, self.reactions[j0]))
        reactions = [s for i,i1,s in sorted(l, reverse=True)]
        reactions += [s for s in self.reactions if s not in reactions]
        end = time.time ()
        self.get_sorted_reactions_elapsed = end-start
        return reactions

    def get_kernel_GJE(self, reactions=None):
        """ Return the kernel K from GJE routine.
        
        Notes
        -----
        The steady state solution is given by ``reactions = K * indep_variables``
        where ``indep_variables = reactions[-K.shape[1]:]``

        Parameters
        ----------
        reactions : list
          When specified then the reaction list defines the order of rows.
          Otherwise the rows are order by the sparsity.

        Returns
        -------
        reactions, kernel : list, Matrix, list
        """
        from sympycore.matrices.linalg import  get_rc_map
        self.compute_kernel_GJE()
        gj, row_operations, leading_rows, leading_cols, zero_rows = self.kernel_GJE_data
        if reactions is None:
            reactions = self.get_sorted_reactions()
        start = time.time ()
        kernel = Matrix(len(reactions), len(reactions)-len(leading_cols))
        indep_vars = [r for r in reactions if r in self.independent_variables]
        dep_vars = [r for r in reactions if r in self.dependent_variables]
        m = len (dep_vars)
        n = len (indep_vars)
        rows = get_rc_map(gj.data)
        def indep_index (r):
            try: return indep_vars.index (r)
            except ValueError: pass
        indep_indices = []
        dep_indices = []
        for r in self.reactions:
            i0 = indep_index (r)
            if i0 is not None:
                indep_indices.append(i0)
                dep_indices.append(None)
            else:
                indep_indices.append(None)
                dep_indices.append(dep_vars.index(r))
        for i0,j0 in zip(leading_rows, leading_cols):
            i = dep_indices[j0]
            for j1 in rows[i0]:
                if j1!=j0:
                    j = indep_indices[j1]
                    kernel[i,j] = -gj.data[(i0,j1)]

        for j in range (n):
            kernel[j+m,j] = 1
        end = time.time()
        self.get_kernel_GJE_elapsed = end-start
        return dep_vars+indep_vars, kernel

    def get_relation_GJE(self, reactions=None):
        """ Return relation matrix R from GJE routine.

        Notes
        -----
        The steady state solution is given by ``dep_fluxes = R * indep_fluxes``

        Parameters
        ----------
        reactions : list
          When specified then the reaction list defines the order of rows.
          Otherwise the rows are order by the sparsity.

        Returns
        -------
        dep_fluxes, indep_fluxes, rmatrix : list, list, Matrix

        See also
        --------
        get_relation_SVD
        """
        reactions, kernel = self.get_kernel_GJE(reactions=reactions)
        start = time.time()
        rank = kernel.shape[0] - kernel.shape[1]
        dep_reactions = reactions[:rank]
        indep_reactions = reactions[rank:]
        r = kernel[:rank]
        end = time.time()
        self.get_relation_GJE_elapsed = end-start
        return dep_reactions, indep_reactions, r

    def get_dense_stoichiometric(self, species, reactions):
        import numpy
        r = numpy.zeros (self.stoichiometric.shape, dtype=float)
        data = self.stoichiometric[:].data # todo: optimize when not transposed
        for (i,j), v in data.iteritems ():
            i1 = species.index (self.species[i])
            j1 = reactions.index (self.reactions[j])
            r[i1,j1] = v
        return r

    def compute_kernel_SVD(self):
        """Compute the kernel of stoichiometric matrix via SVD routine.
        """
        import numpy
        if self.kernel_SVD_data is None:
            array = self.get_dense_stoichiometric (self.species, self.reactions)
            start = time.time ()
            U, s, V = numpy.linalg.svd(array)
            end = time.time()
            self.kernel_SVD_data = U, s, V
            self.compute_kernel_SVD_elapsed = end - start

    def get_kernel_SVD(self, reactions=None):
        """Return the kernel K from SVD routine.

        Notes
        -----
        The steady state solution is given by ``reactions = K * parameters``.
        
        Parameters
        ----------
        reactions : list
          When specified then the reaction list defines the order of rows.
          Otherwise the rows are order by the sparsity.

        Returns
        -------
        reactions, kernel : list, Matrix
        """
        import numpy
        self.compute_kernel_SVD()
        if reactions is None:
            reactions = self.get_sorted_reactions()
        start = time.time ()
        U, s, V = self.kernel_SVD_data
        Vker = V[self.rank:].T
        Vker1 = numpy.zeros (Vker.shape, dtype=float)
        for i, r in enumerate(reactions):
            Vker1[i] = Vker[self.reactions.index(r)]
        end = time.time()
        self.get_kernel_SVD_elapsed = end-start
        return reactions, Vker1

    def get_relation_SVD(self, reactions=None):
        """ Return relation matrix R from SVD routine.

        Notes
        -----
        The steady state solution is given by ``dep_fluxes = R * indep_fluxes``

        Parameters
        ----------
        reactions : list
          When specified then the reaction list defines the order of rows.
          Otherwise the rows are order by the sparsity.

        Returns
        -------
        dep_fluxes, indep_fluxes, rmatrix : list, list, numpy.ndarray
        
        See also
        --------
        get_relation_GJE
        """
        import numpy
        reactions, kernel = self.get_kernel_SVD(reactions=reactions)
        start = time.time ()
        rank = kernel.shape[0]-kernel.shape[1]
        dep_kernel = kernel[:rank]
        indep_kernel = kernel[rank:]
        dep_reactions = reactions[:rank]
        indep_reactions = reactions[rank:]
        r = numpy.dot(dep_kernel, numpy.linalg.inv(indep_kernel))
        end = time.time ()
        self.get_relation_SVD_elapsed = end-start
        return dep_reactions, indep_reactions, r

    def get_relation_SVD_error(self, reactions=None):
        """ Compute maximal relative flux error of the SVD relation routine.

        Notes
        -----
        See the paper for definition.

        Returns
        -------
        rerr : float
        """
        import numpy
        dep_reactions_GJE, indep_reactions_GJE, relation_GJE = self.get_relation_GJE (reactions=reactions)
        dep_reactions_SVD, indep_reactions_SVD, relation_SVD = self.get_relation_SVD (reactions=reactions)
        assert dep_reactions_GJE==dep_reactions_GJE
        assert indep_reactions_GJE==indep_reactions_GJE
        dense_relation_GJE = numpy.zeros(relation_GJE.shape, dtype=float)
        for (i,j),v in relation_GJE.data.iteritems ():
            dense_relation_GJE[i,j]=v
        abserrdata = abs(relation_SVD - dense_relation_GJE).sum (axis=1)
        absdata = numpy.maximum(numpy.maximum(abs(relation_SVD),
                                              abs(dense_relation_GJE)),
                                numpy.ones(relation_SVD.shape)).sum (axis=1)
    
        return max(abserrdata/absdata)

    @classmethod
    def add_boundary_fluxes(cls, matrix, species, reactions, species_info, reactions_info):
        """ Make network open by adding new columns that correspond to
        the boundary fluxes.
        
        Boundary fluxes are defines as fluxes from boundary species
        that enter or leave the network. The names of boundary fluxes
        start with prefix ``BR_``.
        """
        for specie_index in range(len(species)):
            reaction_indices = [j for i,j in matrix if i==specie_index]
            if len (reaction_indices)>1 and\
                not (len(reaction_indices)==2 and len(set(reaction_indices))==1): # to catch polymerization reactions
                continue
            reaction_index = reaction_indices[0]
            stoichiometry = matrix[specie_index, reaction_index]
            specie_id = species[specie_index]
            new_reaction_id = 'BR_%s' % (specie_id)
            new_reaction_index = len(reactions)
            reactions.append(new_reaction_id)
            new_stoichiometry = -1 if stoichiometry>0 else 1
            matrix[specie_index, new_reaction_index] = new_stoichiometry
            if new_stoichiometry>0:
                reactions_info[new_reaction_id]['products'].append(specie_id)
            else:
                reactions_info[new_reaction_id]['reactants'].append(specie_id)
        return matrix, species, reactions, species_info, reactions_info

    @classmethod
    def discard_boundary_species(cls, matrix, species, reactions, species_info, reactions_info):
        """ Make the network open by discarding rows that correspond
        to boundary species.

        Boundary species are defined as the products or reactants of the network.
        """
        boundary_species = []
        extra_reactions = []
        for specie_index in range(len(species)):
            reaction_indices = [j for i,j in matrix if i==specie_index]
            if len(reaction_indices)>1:
                continue
            reaction_index = reaction_indices[0]
            reaction_id = reactions[reaction_index]
            stoichiometry = matrix[specie_index, reaction_index]
            boundary_species.append(specie_index)

        i = 0
        new_matrix = {}
        new_species = []
        for specie_index in range(len(species)):
            if specie_index in boundary_species:
                continue
            new_species.append(species[specie_index])
            for i0, reaction_index in matrix:
                if i0 != specie_index:
                    continue
                new_matrix[i, reaction_index] = matrix[specie_index, reaction_index]
            i += 1
        species = new_species
        matrix = new_matrix

        return matrix, species, reactions, species_info, reactions_info

    @property
    def sparsity_kernel_GJE(self):
        reactions, kernel = self.get_kernel_GJE()
        return len (kernel.data)/(kernel.shape[0]*kernel.shape[1])

    @property
    def sparsity_kernel_SVD(self):
        reactions, kernel = self.get_kernel_SVD()
        return (abs(kernel)>1e-3).sum()/kernel.size

    @property
    def condition_number (self):
        self.compute_kernel_SVD()
        U, s, V = self.kernel_SVD_data        
        return s[0]/s[self.rank-1]

    def matrix_plot(self, matrix, figure_name='matrix_plot.pdf'):
        import numpy
        from matplotlib import pylab
        def _blob(x,y,area,colour):
            hs = numpy.sqrt(area) / 2
            xcorners = numpy.array([x - hs, x + hs, x + hs, x - hs])
            ycorners = numpy.array([y - hs, y - hs, y + hs, y + hs])
            pylab.fill(xcorners, ycorners, colour, edgecolor=colour)
        reenable = False
        if pylab.isinteractive():
            pylab.ioff()
        pylab.clf()
        
        maxWeight = 2**numpy.ceil(numpy.log(numpy.max(numpy.abs(matrix)))/numpy.log(2))
        height, width = matrix.shape
        pylab.fill(numpy.array([0,width,width,0]),numpy.array([0,0,height,height]),'white')
        pylab.axis('off')
        pylab.axis('equal')
        for x in xrange(width):
            for y in xrange(height):
                _x = x+1
                _y = y+1
                w = matrix[y,x]
                if w > 0:
                    _blob(_x - 0.5, height - _y + 0.5, 0.2,'#0099CC')
                elif w < 0:
                    _blob(_x - 0.5, height - _y + 0.5, 0.2,'#660000')

        if reenable:
            pylab.ion()
        pylab.savefig(figure_name) 

    def show_timings(self):
        for a in dir (self):
            if a.endswith ('_elapsed'):
                print '%s took %s seconds' % (a[:-8], getattr (self, a))

    def show_statistics(self, *methods):
        shown = []
        for method in methods:
            assert method in ['GJE', 'SVD'],`method`
            for mthprefix in ['compute_kernel_', 'get_kernel_', 'get_relation_']:
                mthname = mthprefix + method
                mth = getattr(self, mthname)
                mth()
                elapsed = getattr (self, mthname+'_elapsed')
                print '  %s took %.3f seconds' % (mthname, elapsed)
                shown.append(mthname)

        for a in dir (self):
            if a.endswith ('_elapsed'):
                mthname = a[:-8]
                if mthname not in shown:
                    print '%s took %s seconds' % (mthname, getattr (self, a))
