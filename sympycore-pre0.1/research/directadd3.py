def add(a, b):
    if a[0] == '+' and b[0] == '+':
        a = dict(a[1])
        c = a.copy()
        for e, (r, s) in b[1]:
            if e in c:
                p, q = c[e]
                c[e] = (p*s + q*r, q*s)
            else:
                c[e] = (p, q)
        for e, (p, q) in c.items():
            if not p:
                del c[e]
                continue
            x, y = p, q
            while y:
                x, y = y, x % y
            if x != 1:
                c[e] = (p // x, q // x)
        return ('+', frozenset(c.items()))

A = ('+', frozenset((('x', (2, 3)), ('y', (2, 3)), (1, (17, 6)))))
B = ('+', frozenset((('x', (-1, 2)), ('y', (1, 1)), ('z', (3, 2)), (1, (1, 1)))))
add(A, B)