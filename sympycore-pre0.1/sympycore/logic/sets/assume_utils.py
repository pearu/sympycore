
__all__ = ['is_element_of_set', 'is_subset_of_set']

def is_element_of_set(lhs, rhs, assumptions=None):
    r = rhs.try_element(lhs)
    if isinstance(r, bool):
        return r
    #XXX: implement assumptions model

def is_subset_of_set(lhs, rhs, assumptions=None):
    r = rhs.try_subset(lhs)
    if isinstance(r, bool):
        return r
    #XXX: implement assumptions model
