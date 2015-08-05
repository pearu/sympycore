# Introduction #

This document gives an overview of pattern matching rules
that SympyCore implements in various
`matches(pattern, expr, repl_dict={})` methods.
One can use special wild symbols (derived from `BasicWild` class) in defining patterns
to match more general expressions. Wild symbols match
any expression except other wild symbols.

There are two ways to use pattern matching feature:

  * Call `expr.match(pattern)` that returns a dictionary object when `expr` matches `pattern`, otherwise it returns `None`. The dictionary contains the values of wild symbols used in `pattern` such that the following condition holds:
```
expr == pattern.replace_dict(expr.match(pattern))
```

  * Call `pattern.matches(expr, repl_dict={})` that has the same behavior as `expr.match(pattern)` except that `expr` must be `Basic` instance and `repl_dict` may contain predefined wild symbol values. The `matches` methods implement pattern matching rules.

## Matching arithmetic expressions ##

To construct a wild symbol or wild function with arithmetic methods, use `Wild` and `WildFunction` classes.

The following rules are applied when calling `pattern.matches(expr, repl_dict={})`:

  * (A) If `pattern` is a key of `repl_dict` then match is found (ie a copy of `repl_dict` is returned) only if `expr==repl_dict[pattern]` holds.
  * (B) If `pattern` contains no wild symbols then match is found only if `expr==pattern`.
  * (C) If `pattern` is a wild symbol or a wild function then match is found only if either (A) holds or `pattern` is not a key of `repl_dict` in which case the match will be   a copy of `repl_dict` that is updated with `{pattern:expr}`.
  * (C1) By default, wild symbols do not match functions but match everything else.
  * (C2) By default, wild functions do not match arithmetic expression but only `FunctionType` objects.
  * (D1) If `pattern = smth * subpattern` then `subpattern.matches(expr/smth, repl_dict)` is returned (`subpattern` is assumed to contain a wild symbol while `smth` does not contain wild symbols).
  * (D2) If `pattern = smth + subpattern` then `subpattern.matches(expr - smth, repl_dict)` is returned.
  * (D3) If `pattern = subpattern1 + subpattern2` and `expr = subexpr1 + subexpr2` and `d = subpattern1.matches(subexpr2, repl_dict)` is not `None` then `subpattern2.replace_dict(d).matches(subexpr1, d)` is returned. Note that `subexpr2` may also be `0`. While searching for matches of `subpattern1` within `expr` terms, thouse terms with the same coefficents as `subpattern1` are tried first.
  * (E1) If `pattern = subpattern1 ** subpattern2` and `expr` is `Number` instance then `(subpattern2 * Log(subpattern1)).matches(Log(expr), repl_dict)` is returned.
  * (E2) If `pattern = subpattern1 ** subpattern2` and `expr = subexpr1 ** subexpr2` then if `p = subexpr2 / subpattern2` is `Integer` instance then `subpattern1.matches(subexpr1 ** p, repl_dict)` is returned. Else if `d = subpattern1.matches(subexpr1, repl_dict)` is not `None` then `subpattern2.replace_dict(d).matches(subexpr2, d)` is returned.
  * (F1) If `pattern = smth * subpattern` then `subpattern.matches(expr/smth, repl_dict)` is returned.
  * (F2) If `pattern = subpattern1 * subpattern2` then `(Log(subpattern1) + Log(subpattern2)).matches(Log(expr), repl_dict)` is returned (that uses (D3)). Note that here `Log(base ** exponent)` are always expanded to `exponent * Log(base)`.

## Enhancing wild symbols ##

One change the matching properties of wild symbols (or wild functions) using
`predicate` keyword argument to `Wild` (or `WildFunctionType`) constructor.
It's value should be a callable object that takes one argument (a `Basic` instance)
and returns a truth-value. If it returns `False` for given argument then the match
with the wild symbol will be ignored.
```
>>> w=Wild('w')                   # will match arbitrary expressions
>>> w.matches(sympify('x+3'))
{w_: x + 3}
>>> w1=Wild('w1',predicate = lambda expr: expr.is_Atom) # will match only Atom instances
>>> w1.matches(sympify('x+3'))
>>> w1.matches(sympify('x'))
{w1_: x}
>>> w1.matches(sympify('4'))
{w1_: 4}
```


## References ##

http://www.cis.nctu.edu.tw/~wuuyang/papers/A121.ps