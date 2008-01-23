
import sys

__all__ = ['generate_swapped_first_arguments','RedirectOperation']

def get_object_by_name(name, default=None):
    """ Return object that is a value of a variable with name
    in the local or parent namespaces. If variable is found
    in parent namespaces then it is added to children
    namespaces.
    When no variable with name is found then return default
    and add a variable only to the callers locals namespace. 
    """
    frame = sys._getframe(1)
    frames = [frame]
    while frame is not None:
        obj = frame.f_locals.get(name, None)
        if obj is not None:
            for frame in frames:
                frame.f_locals[name] = obj
            return obj
        if default is not None:
            try:
                _name = frame.f_locals['__name__']
            except KeyError:
                _name = None
            if _name is not None and _name=='__main__':
                obj = frames[0].f_locals[name] = default
                return obj
        frames.append(frame)
        frame = frame.f_back
    return default

class RedirectOperation(Exception):
    """ Raised in __nonzero__ methods when the callers
    namespace contains a variable redirect_operation='caller name'.
    If redirect_operation=='ignore_redirection' then no exception is raised.
    
    The caller should catch this exception and return
      self.redirect_operation(<caller arguments>,
                              redirect_operation=redirect_operation)
    """

def not_implemented(*args, **kwargs):
    raise NotImplementedError

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

