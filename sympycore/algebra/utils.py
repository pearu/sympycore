
import new
def swap_first_arguments(func):
    """ Return a function that behaves like func but the
    first arguments are swapped.
    """
    func_code = func.func_code
    co_varnames = func_code.co_varnames
    co_varnames = (co_varnames[1], co_varnames[0]) + co_varnames[2:]
    co_name = func_code.co_name + '_swapped_first_arguments'
    new_code = new.code(func_code.co_argcount,
                        func_code.co_argcount,
                        func_code.co_stacksize,
                        func_code.co_flags,
                        '|\x01\x00|\x00\x00\x02}\x00\x00}\x01\x00'+func_code.co_code,
                        func_code.co_consts,
                        func_code.co_names,
                        co_varnames,
                        func_code.co_filename,
                        co_name,
                        func_code.co_firstlineno,
                        func_code.co_lnotab,
                        func_code.co_freevars,
                        func_code.co_cellvars
                        )
    new_func = new.function(new_code, func.func_globals)
    return new_func
