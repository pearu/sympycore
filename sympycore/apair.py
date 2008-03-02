
class APair(object):
    """ Holds a pair of Python objects.
    """

    __slots__ = ['head', 'data', '_hash']
    _hash = None

    def __new__(cls, head, data, new = object.__new__):
        obj = new(cls)
        obj.head = head
        obj.data = data
        return obj

    def __getitem__(self, index):
        if index is 0: return self.head
        if index is 1: return self.data
        raise IndexError('%s: index %s out of range [0,1]' % (type(cls).__name__, index))

    def __hash__(self):
        h = self._hash
        if not h:
            data = self.data
            if type(data) is dict:
                h = hash(frozenset(data.iteritems()))
            else:
                h = hash(data)
            self._hash = h
        return h
