#!/usr/bin/env python

'''Quine-McCluskey two-level logic minimization method.

Copyright 2004, Robert Dick (dickrp@ece.northwestern.edu).

Routines to compute the optimal sum of products implementation from sets of
don\'t-care terms, minterms, and maxterms.

Command-line usage example:
  qm.py -o1,2,5 -d0,7

Library usage example:
  import qm
  print qm.qm(ones=[1, 2, 5], dc=[0, 7])

Please see the license at the end of the source code for legal information.

Changes:
3 Oct 2007, pearu: add vars keyword argument.
'''


__version__ = '0.1.1'
__author__ = 'Robert Dick (dickrp@ece.northwestern.edu)'


import math


def qm(**kargs):
	'''Compute minimal two-level sum-of-products form.

	Accepts keyword arguments:
	  dc: list of integers specifying don't-care terms
	and either
	  ones: list of minterms
	or
	  zeros: list of maxterms'''

	all = kargs.get('ones', []) + kargs.get('zeros', []) + kargs.get('dc', [])
        vars = kargs.get('vars', None)
        if vars is None:
	    vars = int(math.ceil(math.log(max(all) + 1, 2)))
	elts = 2 << vars
	assert not kargs.get('ones') or not kargs.get('zeros')
	dc = set(b2s(i, vars) for i in kargs.get('dc', []))
	if 'ones' in kargs:
		ones = set(b2s(i, vars) for i in kargs['ones'])
		assert not (ones & dc)
	else:
		zeros = set(b2s(i, vars) for i in kargs['zeros'])
		ones = set(b2s(i, vars) for i in range(elts)) - zeros
		assert not (zeros & dc)
	primes = compute_primes(ones | dc, vars)
	return unate_cover(primes, ones)


def unate_cover(primes, ones):
	'''Return the minimal cardinality subset of primes covering all ones.
	
	Exhaustive for now.  Feel free to replace this with an efficient unate
	covering problem solver.'''

	primes = list(primes)
	cs = min((bitcount(b2s(cubesel, len(primes))), cubesel)
		for cubesel in range(1 << len(primes))
		if is_full_cover(active_primes(cubesel, primes), ones))[1]
	return active_primes(cs, primes)


def active_primes(cubesel, primes):
	'''Return the primes selected by the cube selection integer.'''
	return [prime for used, prime in
		zip(map(int, b2s(cubesel, len(primes))), primes) if used]


def is_full_cover(all_primes, ones):
	'''Return a bool: Does the set of primes cover all minterms?'''
	return min([max([is_cover(p, o) for p in all_primes] + [False])
		for o in ones] + [True])


def is_cover(prime, one):
	'''Return a bool: Does the prime cover the minterm?'''
	return min([p == 'X' or p == o for p, o in zip(prime, one)] + [True])


def compute_primes(cubes, vars):
	'''Compute primes for the given set of cubes and variable count.'''
	sigma = [set(i for i in cubes if bitcount(i) == v)
		for v in range(vars + 1)]
	primes = set()
	while sigma:
		nsigma = []
		redundant = set()
		for c1, c2 in zip(sigma[:-1], sigma[1:]):
			nc = set()
			for a in c1:
				for b in c2:
					m = merge(a, b)
					if m:
						nc.add(m)
						redundant |= set([a, b])
			nsigma.append(nc)
		primes |= set(c for cubes in sigma for c in cubes) - redundant
		sigma = nsigma
	return primes


def bitcount(s):
	'''Return the sum of on bits in s.'''
	return sum(b == '1' for b in s)


def b2s(i, vars):
	'''Convert from an integer to a binary string.'''
	s = ''
	for k in range(vars):
		s = ['0', '1'][i & 1] + s
		i >>= 1
	return s


def merge(i, j):
	'''Return cube merge.  'X' is don\'t-care.  'None' if merge impossible.'''
	s = ''
	dif_cnt = 0
	for a, b in zip(i, j):
		if (a == 'X' or b == 'X') and a != b:
			return None
		elif a != b:
			dif_cnt += 1
			s += 'X'
		else:
			s += a
		if dif_cnt > 1:
			return None
	return s


if __name__ == '__main__':
	from optparse import *
	from sys import *

	def main():
		options = [
			Option('-d', '--dontcares', dest='dc', default='',
				help='comma-separated don\'t-cares', metavar='D'),
			Option('-o', '--ones', dest='ones', default='',
				help='comma-separated ones', metavar='O'),
			Option('-z', '--zeros', dest='zeros', default='',
				help='comma-separated zeros', metavar='Z')
		]

		f = IndentedHelpFormatter()
		def raw_format(s): return s + '\n'
		f.format_description = raw_format

		optparser = OptionParser(description=__doc__, formatter=f)
		optparser.add_options(options)
		opts, args = optparser.parse_args()
		if len(argv) == 1 or args:
			optparser.print_help()
			exit()
		
		opts.dc = [int(i) for i in opts.dc.split(',') if i]
		opts.ones = [int(i) for i in opts.ones.split(',') if i]
		opts.zeros = [int(i) for i in opts.zeros.split(',') if i]
	
		soln = qm(dc=opts.dc, ones=opts.ones, zeros=opts.zeros)
		if len(soln) == 0:
			stdout.write('contradiction\n')			
		elif len(soln) == 1 and soln[0].count('X') == len(soln[0]):
			stdout.write('tautology\n')
		else:
			stdout.write(' '.join(soln) + '\n')

	main()
