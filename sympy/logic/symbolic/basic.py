
from ...core import Basic
from ...core.utils import memoizer_immutable_args

__all__ = ['BasicBoolean']

class BasicBoolean(Basic):

    def is_subset_of(self, other):
        """ Returns True if from other follows self.
        """
        return False
    def is_opposite_to(self, other):
        """ Returns True if from not other follows self.
        """
        return False
    def intersection_subset(self, other):
        """ Assume that self = smth xor smth2 and other = smth xor smth3.
        Return smth or None.
        """
        return
    def minus_subset(self, other, negative=False):
        """ Assume self = smth xor other. Return smth or None.
        """
        return
    def truth_table(self, atoms=None):
        """ Compute truth table of boolean expression.

        Return (atoms, table) where table is a map
          {<tuple of boolean values>: <self truth value>}
        and atoms is a list conditions and boolean
        symbols.
        """
        if atoms is None:
            atoms = list(self.atoms(Boolean).union(self.conditions()))
        n = len(atoms)
        r = range(n-1, -1, -1)
        table = {}
        for i in range(2**n):
            # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/219300
            bvals =  tuple(map(lambda y:bool((i>>y)&1), r))
            table[bvals] = self.replace_list(atoms, bvals)
        return atoms, table


    @memoizer_immutable_args('BooleanMeths.compute_truth_table')
    def compute_truth_table(self):
        """ Compute full truth table.

        Return (atoms, table) where table is a map
          {<integer value>: <list of boolean values>}
        where integer value is obtained from binary representation
        of boolean values. The table contains only combinations
        of boolean values that evaluate self to True.
        """        
        conditions = sorted(self.conditions())
        atoms = sorted(self.atoms(Boolean))
        table = {}
        if conditions:
            bsyms = [DummyBoolean('b%s' % (i)) for i in range(len(conditions))]
            expr = self.replace_list(conditions, bsyms)
            syms = map(str, atoms + bsyms)
        else:
            expr = self
            syms = map(str, atoms)
        n = len(syms)
        r = range(n-1,-1,-1)
        string_expr = expr.tostr()
        l_dict = {'XOr':XOr,'And':And,'Or':Or,'Not':Not}
        for i in range(2**n):
            bvals =  map(lambda y:bool((i>>y)&1), r)
            dvals = {}
            for s,b in zip(syms, bvals):
                dvals[s] = b
            v = eval(string_expr, dvals, l_dict)
            if v is True:
                table[i] = bvals
            else:
                assert isinstance(v, bool),`v`
        return atoms + conditions, table
    def test(self, test):
        """
        Return conditions when test holds assuming that self is True.
        """
        test = sympify(test)
        if isinstance(test, bool): return test
        atoms, table = self.compute_truth_table()
        if not table:
            raise ValueError('assumption expression %r is never True' % (str(self)))
        t_atoms = sorted(test.atoms(Boolean).union(test.conditions()))
        n = len(atoms)
        indices = []
        for i in range(n):
            a = atoms[i]
            if a in t_atoms:
                continue
            flag = True
            for t in t_atoms:
                if t.is_subset_of(a) or a.is_subset_of(t):
                    flag = False
                    break
            if flag:
                indices.append(i)
        r = range(n-1, -1, -1)
        l = []
        for bvals in table.values():
            t = test.replace_list(atoms, bvals)
            if t is False:
                continue
            if t is True and indices:
                bvals = bvals[:]
                for i in indices:
                    bvals[i] = atoms[i]
                t = self.replace_list(atoms, bvals)
            l.append(t)
        if not l:
            return False
        return And(*l)
    def conditions(self, type=None):
        """
        Return a set of Condition instances.
        """
        if type is None: type = Condition
        s = set()
        if isinstance(self, type):
            s.add(self)
        for obj in self:
            if isinstance(obj, classes.Predicate):
                s = s.union(obj.conditions(type=type))
        return s
    def minimize(self):
        """ Return minimal boolean expression using Quine-McCluskey algorithm.

        See
            http://en.wikipedia.org/wiki/Quine-McCluskey_algorithm

        Note:
          The algorithm does not know about XOR operator. So, expressions
          containing XOr instances may not be minimal.
        """
        atoms, table = self.compute_truth_table()
        n = len(atoms)
        l = []
        r = range(n)
        q = qm(ones=table.keys(), vars=n)
        for t in q:
            p = []
            for c,i in zip(t,r):
                if c=='0': p.append(Not(atoms[i]))
                elif c=='1': p.append(atoms[i])
            l.append(And(*p))
        return Or(*l)

