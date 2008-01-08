import types

iterator_types = (type(iter([])), type(iter(())), type(iter(frozenset())),
                  type(dict().iteritems()), types.GeneratorType)

class Pairs(object):
    """ Base class for holding pairs (by default non-commutative).
    """
    def __new__(cls, pairs):
        if isinstance(pairs, cls):
            return pairs
        o = object.__new__(cls)
        o._pairs = pairs
        o._hash = None
        return o

    @property
    def pairs(self):
        """ Return pairs as a tuple.
        """
        pairs = self._pairs
        if not isinstance(pairs, tuple):
            self._pairs = pairs = tuple(pairs)
        return pairs

    def __iter__(self):
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = tuple(pairs)
            return pairs
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = tuple(pairs)
            return len(pairs)
        return len(pairs)

    def __eq__(self, other):
        if type(self) is type(other):
            return self.pairs == other.pairs
        return False

    #XXX: impl modification methods


class CommutativePairs(Pairs):
    """ Represents operands of an commutative operation.

      CommutativePairs(<pairs>)

    where <pairs> is a sequence or an iterator of pairs:

      (<expression>, <repetition>)

    Here <expression> must be hashable as internally the pairs are
    saved in Python dictionary for update efficiency.

    CommutativePairs instance is mutable until the moment its hash
    value is computed.

    The following methods are defined to modify the CommutativePairs
    instance:
      _add_value(rhs, one, zero)
        rhs must be usable as key

      _add_values(rhs, one, zero)
        rhs must be an iterable returning pairs

      _multiply_values(rhs, one, zero)
        rhs must be support multiplication with values

      _expand_multiply_values(rhs, one, zero)
        rhs must be an iterable returning pairs
        
      _add_keys(rhs, one, zero)
        rhs must support addition with keys
    """
    
    @property
    def pairs(self):
        """ Return pairs as mutable dictionary.
        """
        pairs = self._pairs
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs

    def __iter__(self):
        """ Return iterator of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return pairs.iteritems()
        elif isinstance(pairs, dict):
            return pairs.iteritems()
        elif isinstance(pairs, Pairs):
            raise
            return pairs.pairs
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return len(pairs)
        elif isinstance(pairs, Pairs):
            raise
            return pairs.length()
        return len(pairs)

    def __hash__(self):
        h = self._hash
        if h is None:
            # Using frozenset hash algorithm to avoid creating
            # frozenset instance. It should be safe to have the
            # same hash value with the frozenset as dictionary
            # keys of self should never contain a frozenset.
            h = 1927868237
            h *= self.length()+1
            for t in self:
                h1 = hash(t)
                h ^= (h1 ^ (h1 << 16) ^ 89869747)  * 3644798167
            h = h * 69069 + 907133923
            self._hash = h
        return h

    def __str__(self):
        return '%s([%s])' % (self.__class__.__name__,
                             ', '.join(['(%s, %s)' % tc for tc in self.pairs.iteritems()]))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._pairs)

    def _add_value(self, rhs, one, zero):
        h = self._hash
        if h is not None:
            raise TypeError('cannot add value to immutable pairs inplace'\
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

    def _add_values(self, rhs, one, zero):
        h = self._hash
        if h is not None:
            raise TypeError('cannot add values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t,c in rhs:
            b = pairs.get(t)
            if b is None:
                pairs[t] = c
            else:
                c = b + c
                if c==zero:
                    del pairs[t]
                else:
                    pairs[t] = c

    def _multiply_values(self, rhs, one, zero):
        h = self._hash
        if h is not None:
            raise TypeError('cannot multiply values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t in pairs.keys():
            pairs[t] *= rhs

    def _expand_multiply_values(self, rhs, one, zero):
        h = self._hash
        if h is not None:
            raise TypeError('cannot expand multiply values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        self._pairs = d = {}
        if isinstance(rhs, iterator_types):
            seq1 = rhs
            seq2 = pairs.items()
        elif len(rhs) > len(pairs):
            seq1 = pairs.iteritems()
            seq2 = rhs
        else:
            seq1 = rhs
            seq2 = pairs.items()
        for t1, c1 in seq1:
            for t2, c2 in seq2:
                t = t1 * t2
                c = c1 * c2
                #XXX: make sure that t is not a number, it can be one though
                b = d.get(t)
                if b is None:
                    d[t] = c
                else:
                    c = b + c
                    if c==0:
                        del d[t]
                    else:
                        d[t] = c

    def _add_keys(self, rhs, one, zero):
        h = self._hash
        if h is not None:
            raise TypeError('cannot add keys to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs        
        self._pairs = d = {}
        for t,c in pairs.items():
            d[t + rhs] = c
        self._pairs = d
