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

    """

    def __init__(self, pairs):
        self._pairs = pairs
        self._hash = None

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
        pairs = self._pairs
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs[key]

    def __setitem__(self, key, item):
        h = self._hash
        if h is not None:
            raise TypeError('cannot set item to immutable %s instance'\
                            ' (hash has been computed)'\
                            % (self.__class__.__name__))
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs.__setitem__(key, item)

    def __delitem__(self, key):
        h = self._hash
        if h is not None:
            raise TypeError('cannot delete item in immutable %s instance'\
                            ' (hash has been computed)'\
                            % (self.__class__.__name__))
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs.__delitem__(key)

    def __hash__(self):
        h = self._hash
        if h is None:
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
