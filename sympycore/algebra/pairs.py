
class Pairs(object):
    """ Base class for holding pairs (by default non-commutative).
    """
    def __init__(self, pairs):
        self._pairs = pairs
        self._hash = None

    @property
    def pairs(self):
        """ Return pairs as a tuple.
        """
        pairs = self._pairs
        if not isinstance(pairs, tuple):
            self._pairs = pairs = tuple(pairs)
        return pairs

    def iterator(self):
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

class CommutativePairs(Pairs):

    @property
    def pairs(self):
        """ Return pairs as mutable dictionary.
        """
        pairs = self._pairs
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs

    def iterator(self):
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return pairs.iteritems()
        elif isinstance(pairs, dict):
            return pairs.iteritems()
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return len(pairs)
        return len(pairs)
