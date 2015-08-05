
from basic import Basic, sympify

class Assumptions(tuple):

    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def check_positive(self, expr):
        for assume in self:
            print assume
            if assume.lhs==expr:
                if assume.condition.rhs.is_positive:
                    return True

Basic.Assumptions = Assumptions
