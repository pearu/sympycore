import types

iterator_types = (type(iter([])), type(iter(())), type(iter(frozenset())),
                  type(dict().iteritems()), types.GeneratorType)

class CommutativePairs:
    """ Represents operants of an commutative operation.

    CommutativePairs(<pairs>)

    where <pairs> is a sequence or an iterator of pairs:

      (<expression>, <repetition>)

    Here <expression> must be hashable as internally the pairs
    are saved in Python dictionary for update efficiency.

    CommutativePairs instance is mutable until the moment
    its hash value is computed.

    For a mutable CommutativePairs instance the following
    methods are available:
      sum_add_element(rhs, one, zero)
      sum_add_number(rhs, one, zero)
      sum_add_sum(rhs, one, zero)
      sum_multiply_number(rhs, one, zero)
      sum_multiply_sum(rhs, one, zero)
      sum_power_exponent(exp, one, zero)
      
      product_multiply_element(rhs, one, zero)
      product_multiply_product(rhs, one, zero)
      product_power_exponent(exp, one, zero)
    """

    def __init__(self, pairs):
        self._pairs = pairs
        self._hash = None

    @property
    def pairs(self):
        """ Return pairs as mutable dictionary.
        """
        pairs = self._pairs
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs

    def __iter__(self):
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return pairs.iteritems()
        elif isinstance(pairs, dict):
            return pairs.iteritems()
        return iter(pairs)

    def __len__(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return len(pairs)
        return len(pairs)

    def __getitem__(self, key):
        return self.pairs[key]

    def __setitem__(self, key, item):
        h = self._hash
        if h is not None:
            raise TypeError('cannot set item to immutable %s instance'\
                            ' (hash has been computed)')
        self.pairs[key] = item

    def __delitem__(self, key):
        h = self._hash
        if h is not None:
            raise TypeError('cannot delete item in immutable %s instance'\
                            ' (hash has been computed)')
        del self.pairs[key]

    def __hash__(self):
        h = self._hash
        if h is None:
            #self._hash = h = hash(frozenset(self.pairs))
        #elif 0:
            # Using frozenset hash algorithm to avoid creating
            # frozenset instance. It should be safe to have the
            # same hash value with the frozenset as dictionary
            # keys of self should never contain a frozenset.
            h = 1927868237
            h *= len(self)+1
            for t in iter(self):
                h1 = hash(t)
                h ^= (h1 ^ (h1 << 16) ^ 89869747)  * 3644798167
            h = h * 69069 + 907133923
            self._hash = h
        return h

    def __str__(self):
        return '%s([%s])' % (self.__class__.__name__, ', '.join(['(%s, %s)' % tc for tc in self]))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._pairs)

    def sum_add_element(self, rhs, one, zero):
        """ Perform the following in-place operation on self:

        AlgebraicExpression(TERMS, <self>) + <rhs>

        <rhs> must be AlgebraicExpression instance.
        """
        h = self._hash
        if h is not None:
            raise TypeError('cannot add immutable sum inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        b = pairs.get(rhs)
        if b is None:
            pairs[rhs] = one
        else:
            c = b + one
            if c==zero:
                del pairs[rhs]
            else:
                pairs[rhs] = c

    def sum_add_number(self, rhs, one, zero):
        """ Perform the following in-place operation on self:

        AlgebraicExpression(TERMS, <self>) + AlgebraicExpression(NUMBER, <rhs>)

        """
        return self.sum_add_element(one, rhs, zero)
        h = self._hash
        if h is not None:
            raise TypeError('cannot add immutable sum inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        b = pairs.get(one)
        if b is None:
            pairs[one] = rhs
        else:
            c = b + rhs
            if c==zero:
                del pairs[one]
            else:
                pairs[one] = c        

    def sum_add_sum(self, rhs, one, zero):
        """ Perform the following in-place operation on self:

        AlgebraicExpression(TERMS, <self>) + AlgebraicExpression(TERMS, <rhs>)
        """
        h = self._hash
        if h is not None:
            raise TypeError('cannot add immutable sum in-place'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t,c in rhs:
            b = pairs.get(t)
            if b is None:
                pairs[t] = c
            else:
                c = b + c
                if c==0:
                    del pairs[t]
                else:
                    pairs[t] = c

    def sum_multiply_number(self, rhs, one, zero):
        """ Perform the following in-place operation on self:

        AlgebraicExpression(TERMS, <self>) * AlgebraicExpression(NUMBER, <rhs>)
        """
        h = self._hash
        if h is not None:
            raise TypeError('cannot multiply immutable sum in place'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t in pairs.keys():
            pairs[t] *= rhs

    def sum_multiply_sum(self, rhs, one, zero):
        """ Perform the following in-place operation on self:

        AlgebraicExpression(TERMS, <self>) * AlgebraicExpression(TERMS, <rhs>)

        The product is expanded.
        """
        h = self._hash
        if h is not None:
            raise TypeError('cannot add immutable sum in-place'\
                            ' (hash has been computed)')
        pairs = self.pairs
        self._pairs = d = {}
        if isinstance(rhs, iterator_types):
            seq1 = rhs
            seq2 = pairs
        elif len(rhs) > len(pairs):
            seq1 = pairs
            seq2 = rhs
        else:
            seq1 = rhs
            seq2 = pairs
        for t1, c1 in seq1:
            for t2, c2 in seq2:
                t = t1 * t2
                c = c1 * c2
                #XXX: make sure that t is not a number
                b = d.get(t)
                if b is None:
                    d[t] = c
                else:
                    c = b + c
                    if c==0:
                        del d[t]
                    else:
                        d[t] = c

    def sum_power_exponent(self, exp, one, zero):
        """ Perform the following in-place operation on self:

          AlgebraicExpression(TERMS, <self>) ** <exp>

        <exp> must be a positive integer.
        The power is expanded.
        """        
        h = self._hash
        if h is not None:
            raise TypeError('cannot multiply immutable product inplace'\
                            ' (hash has been computed)')

        tc = list(self.pairs)
        self._pairs = r = {}

        ## Consider polynomial
        ##   P(x) = sum_{i=0}^n p_i x^k
        ## and its m-th exponent
        ##   P(x)^m = sum_{k=0}^{m n} a(m,k) x^k
        ## The coefficients a(m,k) can be computed using the
        ## J.C.P. Miller Pure Recurrence [see D.E.Knuth,
        ## Seminumerical Algorithms, The art of Computer
        ## Programming v.2, Addison Wesley, Reading, 1981;]:
        ##  a(m,k) = 1/(k p_0) sum_{i=1}^n p_i ((m+1)i-k) a(m,k-i),
        ## where a(m,0) = p_0^m.
        
        m = int(p)
        n = len(tc)-1
        t0,c0 = tc[0]
        """
        p0 = [s_mul(s_mul(t, s_power(t0,-one)),(NUMBER, c/c0)) for t,c in tc]

        add_inplace_dict(r, s_power(t0,p), c0**m)
        l = [terms_dict_to_expr(r)]
        for k in xrange(1, m * n + 1):
            r1 = dict()
            for i in xrange(1, min(n+1,k+1)):
                nn = (m+1)*i-k
            if nn:
                add_inplace_dict(r1, expand_mul(l[k-i], p0[i]), Fraction(nn, k))
        f = terms_dict_to_expr(r1)
        add_inplace_dict1(r, f)
        l.append(f)
        return terms_dict_to_expr(r)
        """
        raise NotImplementedError
        
    def product_multiply_element(self, rhs, one, zero):
        """ Perform the following in-place operation on self:

        AlgebraicExpression(FACTORS, <self>) * <rhs>

        <rhs> must be AlgebraicExpression instance.
        """
        h = self._hash
        if h is not None:
            raise TypeError('cannot multiply immutable product inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        b = pairs.get(rhs)
        if b is None:
            pairs[rhs] = one
        else:
            c = b + one
            if c==zero:
                del pairs[rhs]
            else:
                pairs[rhs] = c

    def product_multiply_product(self, rhs, one, zero):
        """ Perform the following in-place operation on self:

        AlgebraicExpression(FACTORS, <self>) * AlgebraicExpression(FACTORS, <rhs>)
        """
        h = self._hash
        if h is not None:
            raise TypeError('cannot multiply immutable product in-place'\
                            ' (hash has been computed)')
        pairs = self.pairs        
        for t,c in rhs:
            b = pairs.get(t)
            if b is None:
                pairs[t] = c
            else:
                c = b + c
                if c==0:
                    del pairs[t]
                else:
                    pairs[t] = c

    def product_power_exponent(self, exp, one, zero):
        """ Perform the following in-place operation on self:

          AlgebraicExpression(FACTORS, <self>) ** <exp>

        <exp> must be a number.
        """
        h = self._hash
        if h is not None:
            raise TypeError('cannot take a power of immutable product in-place'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t in pairs.keys():
            pairs[t] = pairs[t] * exp
