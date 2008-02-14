
from collections import defaultdict

h1 = intern('H1')
h2 = intern('H2')
h3 = intern('H3')
h4 = intern('H4')

c = lambda: None

h1_d = defaultdict(c,
                   {h1: c,
                    h2: c,
                    h3: c},
                   )

h2_d = defaultdict(lambda : c,
                   {h1: c,
                    h2: c,
                    h3: c},
                   )

h3_d = defaultdict(lambda : c,
                   {h1: c,
                    h2: c,
                    h3: c},
                   )

h4_d = defaultdict(lambda : c,
                   {h1: c,
                    h2: c,
                    h3: c},
                   )

d = defaultdict(lambda : h4_d,
                {h1: h1_d,
                h2: h2_d,
                h3: h3_d},
                )

def bar():
    #a,b = h1,h1 # best case
    a,b = h4,h4 # worst case
    return d[a][b]

def foo(h1=h1, h2=h2, h3=h3, h4=4):
    #a,b = h1,h1 # best case
    a,b = h4,h4 # worst case
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return

def fun1():
    if 1:
        return

def fun2():
    if 1:
        return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    if a is h1:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h2:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    elif a is h3:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
    else:
        if b is h1:
            pass
        elif b is h2:
            pass
        elif b is h3:
            pass
        else:
            return
