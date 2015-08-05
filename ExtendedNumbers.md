Extended numbers as implemented by the ExtendedNumber class are a shortcut to describing limits. As currently implemented, ExtendedNumbers have two properties: direction (a number with magnitude 1, or 0 for undefined) and magnitude (infinite/undefined). Either property can be defined independently of the other (although ExtendedNumbers with defined direction and undefined magnitude are not currently used, and it is unclear whether they would be useful).

Not-a-number (nan, undefined) has both undefined magnitude and direction. Any operation with nan, except  for application of a function that is constant, has undefined result.

Infinities have infinite magnitude and may have either defined or undefined direction. An infinity may be defined as the value of 1/r in the limit r->0. The result depends on the direction of approach: if r approaches 0 from the positive direction, 1/r tends to +oo, and if it approaches from the negative direction, it tends to -oo. If r approaches along a line in the complex plane, the correct result is oo times the complex direction. If the approach is nonlinear (e.g. a complex spiral), or if unknown, the result has undefined direction. The operation x/0 where x is an arbitrary nonzero real or complex number should result in undirected infinity, because although the magnitude is well-defined, the direction of approach to 0 is unknown.

Note that undirected infinity can be interpreted either as a projective real infinity or as a projective complex infinity, depending on the context.

Operations on extended numbers should be defined so as to preserve correct results in the composition of limits. When an evaluation is ambiguous, the result should be entirely or partially undefined. Following this convention permits limits to be computed by first attempting to evaluate an expression directly, and only fall back to the full limit algorithm if the result is undefined. However, some exceptions may be necessary for convenience reasons. For example, we need 0\*x -> 0 for symbolic x, even though strictly this should result in an undefined result if x is replaced by an ExtendedNumber instead of a regular number.

### Addition table of extended numbers ###
| `+`       | -oo       | number    | +oo       | zoo       | undefined |
|:----------|:----------|:----------|:----------|:----------|:----------|
| -oo       | -oo       | -oo       | undefined | undefined | undefined |
| number    | -oo       | num1+num2 | +oo       | zoo       | undefined |
| +oo       | undefined | +oo       | +oo       | undefined | undefined |
| zoo       | undefined | zoo       | undefined | undefined | undefined |
| undefined | undefined | undefined | undefined | undefined | undefined |

### Multiplication table of extended numbers ###
| `*`       | -oo       | +oo       | zoo       | undefined |
|:----------|:----------|:----------|:----------|:----------|
| -oo       | +oo       | -oo       | zoo       | undefined |
| negative  | +oo       | -oo       | zoo       | undefined |
| 0         | undefined | undefined | undefined | undefined |
| positive  | -oo       | +oo       | zoo       | undefined |
| +oo       | -oo       | +oo       | zoo       | undefined |
| zoo       | zoo       | zoo       | zoo       | undefined |
| undefined | undefined | undefined | undefined | undefined |

Multiplication of complex and extended numbers is defined by multiplication
of real/imag parts with extended numbers.

### Power table of extended numbers ###
| `**`        | -oo       | +oo       | zoo       | undefined |
|:------------|:----------|:----------|:----------|:----------|
| -oo         | 0         | zoo       | undefined | undefined |
| negative<-1 | 0         | zoo       | undefined | undefined |
| -1          | undefined | undefined | undefined | undefined |
| negative>-1 | zoo       | 0         | undefined | undefined |
| 0           | zoo       | 0         | undefined | undefined |
| positive<1  | zoo       | 0         | undefined | undefined |
| 1           | 1         | 1         | 1         | 1 or undefined |
| positive>1  | 0         | +oo       | undefined | undefined |
| +oo         | 0         | +oo       | undefined | undefined |
| zoo         | 0         | zoo       | undefined | undefined |
| undefined   | undefined | undefined | undefined | undefined |

| `**`        | negative  | 0         | positive            |
|:------------|:----------|:----------|:--------------------|
| -oo         | 0         | 1         | `(-1)**positive * oo` |
| +oo         | 0         | 1         | +oo                 |
| zoo         | 0         | 1         | zoo                 |
| undefined   | undefined | 1         | undefined           |