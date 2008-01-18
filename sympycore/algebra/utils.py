
__all__ = ['generate_swapped_first_arguments']

def generate_swapped_first_arguments(func):
    """ Creates a new function from func by swapping its
    first arguments and parts of its name. For example, if

      def foo_LHS_RHS(lhs, rhs, rest):
          ...

    then calling

      generate_swapped_first_arguments(foo_LHS_RHS)

    is equivalent to defining

      def foo_RHS_LHS(rhs, lhs, rest):
          return foo_LHS_RHS(lhs, rhs, rest)
    
    """
    fn = func.func_code.co_filename
    if fn.endswith('.pyc'):
        fn = fn[:-1]
    fl = func.func_code.co_firstlineno
    f = open(fn,'r')
    for i in xrange(fl-1):
        f.readline()
    code_lines = [f.readline()]
    while 1:
        l = f.readline()
        if l[:1].strip():
            break
        code_lines.append(l)
    f.close()
    first_line = code_lines[0]
    i = first_line.index('(')
    name = first_line[3:i].strip()
    l = name.split('_')
    if len(l)<3:
        return
    new_name = '_'.join(l[:-2] + [l[-1], l[-2]])
    l = first_line[i+1:].split(',')
    new_args = '(' + ','.join([l[1].strip(),l[0].strip()]+l[2:])
    code_lines = ['def %s%s' % (new_name, new_args)] + code_lines[1:]
    code = ''.join(code_lines)
    exec code in func.func_globals

