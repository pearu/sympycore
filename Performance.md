_This page is automatically generated. Do not edit this page!_

See http://sympycore.googlecode.com/svn/tools/gen_performance_page.py .

Last update: Tue Jul 29 11:44:02 2008

|                                                                  **Executed code** | **sympy (with caching)** | **sympycore** | **Speed-up** |
|:-----------------------------------------------------------------------------------|:-------------------------|:--------------|:-------------|
|                                               `Add(x,<random integer>,y)`, 2000x   |            0.1308 secs   | 0.0333 secs   |    3.9297x   |
|                                               `Mul(x,<random integer>,y)`, 2000x   |            0.1987 secs   | 0.0467 secs   |    4.2566x   |
|                                                           `sum(x**i/i,i=1..400)`   |            1.0042 secs   | 0.0054 secs   |  184.8658x   |
|                                                 `expand((x+z+y)**20 * (z+x)**9)`   |            1.0249 secs   | 0.0140 secs   |   73.3942x   |
|                                                          `expand((2+3*I)**1000)`   |            0.0013 secs   | 0.0002 secs   |    7.2520x   |
|                                                        `expand((2+3*I/4)**1000)`   |            0.0140 secs   | 0.0086 secs   |    1.6164x   |
|                                                         `sin(n*pi/6), n=0...100`   |            0.0630 secs   | 0.0029 secs   |   21.5810x   |
|                        `e.subs(x,z).subs(y,z) where e = expand((x+2*y+3*z)**20)`   |            0.0563 secs   | 0.0047 secs   |   11.9829x   |
|                                    `(sin(1+pi)**2 + 3**sqrt(1+pi**2)).evalf(30)`   |            0.0007 secs   | 0.0007 secs   |    0.9876x   |
|                                   `(sin(1+pi)**2 + 3**sqrt(1+pi**2)).evalf(300)`   |            0.0032 secs   | 0.0045 secs   |    0.7230x   |
|                                `str(e) where e = <randint> * (x+2*y+3*z), 1000x`   |            1.7177 secs   | 0.0281 secs   |   61.1084x   |
|                                       `str(e) where e = expand((x+2*y+3*z)**50)`   |            3.9265 secs   | 0.0400 secs   |   98.1972x   |
|                            `f=4*x**3+y**2*x**2+x+1, f=integrate(f) for i=1...10`   |            0.0149 secs   | 0.0018 secs   |    8.1026x   |
|                         `f=(x/(1+sin(x**(y+x**2)))**2), f=f.diff(x) for i=1...5`   |            0.6893 secs   | 0.0791 secs   |    8.7162x   |
| `expr.match(pattern), where expr=(x*y**2)**sin(x+y**2), pattern=(v*w)**sin(v+w)`   |            0.0019 secs   | 0.0003 secs   |    6.1977x   |
|                   polynomial division P/Q, P,Q have roots (1,2,3,4,5), (1,2,3/4)   |            0.0300 secs   | 0.0010 secs   |   30.1408x   |
|                                                  Run sympy/examples/fem\_test.py.  |                    N/A   | 0.0595 secs   |        N/A   |

|                                                                  **Executed code** |  **swiginac** | **sympycore** | **Speed-up** |
|:-----------------------------------------------------------------------------------|:--------------|:--------------|:-------------|
|                                               `Add(x,<random integer>,y)`, 2000x   | 0.2078 secs   | 0.0333 secs   |    6.2427x   |
|                                               `Mul(x,<random integer>,y)`, 2000x   | 0.1160 secs   | 0.0467 secs   |    2.4861x   |
|                                                           `sum(x**i/i,i=1..400)`   | 0.1932 secs   | 0.0054 secs   |   35.5741x   |
|                                                 `expand((x+z+y)**20 * (z+x)**9)`   | 0.0177 secs   | 0.0140 secs   |    1.2647x   |
|                                                          `expand((2+3*I)**1000)`   | 0.0001 secs   | 0.0002 secs   |    0.7062x   |
|                                                        `expand((2+3*I/4)**1000)`   | 0.0007 secs   | 0.0086 secs   |    0.0823x   |
|                                                         `sin(n*pi/6), n=0...100`   | 0.0087 secs   | 0.0029 secs   |    2.9807x   |
|                        `e.subs(x,z).subs(y,z) where e = expand((x+2*y+3*z)**20)`   | 0.0040 secs   | 0.0047 secs   |    0.8479x   |
|                                    `(sin(1+pi)**2 + 3**sqrt(1+pi**2)).evalf(30)`   | 0.0001 secs   | 0.0007 secs   |    0.1993x   |
|                                   `(sin(1+pi)**2 + 3**sqrt(1+pi**2)).evalf(300)`   |         N/A   | 0.0045 secs   |        N/A   |
|                                `str(e) where e = <randint> * (x+2*y+3*z), 1000x`   | 0.0169 secs   | 0.0281 secs   |    0.6022x   |
|                                       `str(e) where e = expand((x+2*y+3*z)**50)`   | 0.0075 secs   | 0.0400 secs   |    0.1870x   |
|                            `f=4*x**3+y**2*x**2+x+1, f=integrate(f) for i=1...10`   |         N/A   | 0.0018 secs   |        N/A   |
|                         `f=(x/(1+sin(x**(y+x**2)))**2), f=f.diff(x) for i=1...5`   | 0.0095 secs   | 0.0791 secs   |    0.1202x   |
| `expr.match(pattern), where expr=(x*y**2)**sin(x+y**2), pattern=(v*w)**sin(v+w)`   |         N/A   | 0.0003 secs   |        N/A   |
|                   polynomial division P/Q, P,Q have roots (1,2,3,4,5), (1,2,3/4)   |         N/A   | 0.0010 secs   |        N/A   |
|                                                  Run sympy/examples/fem\_test.py.  |         N/A   | 0.0595 secs   |        N/A   |

Notes:
  1. Speed-up is inverse ratio between the last column timing and the minimum of rest of columns.
  1. swiginac does not support precision parameter in evalf
  1. swiginac objects don not have integrate method
  1. swiginac match does not handle given case