Help on module qm:

NAME
    qm - Quine-McCluskey two-level logic minimization method.

FILE
    /home/dickrp/unison/python/mature/qm/qm.py

DESCRIPTION
    Copyright 2004, Robert Dick (dickrp@ece.northwestern.edu).
    
    Routines to compute the optimal sum of products implementation from sets of
    don't-care terms, minterms, and maxterms.
    
    Command-line usage example:
      qm.py -o1,2,5 -d0,7
    
    Library usage example:
      import qm
      print qm.qm(ones=[1, 2, 5], dc=[0, 7])
    
    Please see the license at the end of the source code for legal information.

FUNCTIONS
    active_primes(cubesel, primes)
        Return the primes selected by the cube selection integer.
    
    b2s(i, vars)
        Convert from an integer to a binary string.
    
    bitcount(s)
        Return the sum of on bits in s.
    
    compute_primes(cubes, vars)
        Compute primes for the given set of cubes and variable count.
    
    is_cover(prime, one)
        Return a bool: Does the prime cover the minterm?
    
    is_full_cover(all_primes, ones)
        Return a bool: Does the set of primes cover all minterms?
    
    merge(i, j)
        Return cube merge.  'X' is don't-care.  'None' if merge impossible.
    
    qm(**kargs)
        Compute minimal two-level sum-of-products form.
        
        Accepts keyword arguments:
          dc: list of integers specifying don't-care terms
        and either
          ones: list of minterms
        or
          zeros: list of maxterms
    
    unate_cover(primes, ones)
        Return the minimal cardinality subset of primes covering all ones.
        
        Exhaustive for now.  Feel free to replace this with an efficient unate
        covering problem solver.

DATA
    __author__ = 'Robert Dick (dickrp@ece.northwestern.edu)'
    __version__ = '0.1'

VERSION
    0.1

AUTHOR
    Robert Dick (dickrp@ece.northwestern.edu)


