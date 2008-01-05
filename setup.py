
from distutils.core import Extension

c_sexpr_ext = Extension('sympycore.arithmetic.c_sexpr',
                        sources = ['sympycore/arithmetic/src/sexpr.c']
                        )

c_iutils_ext = Extension('sympycore.arithmetic.integer_utils',
                        sources = ['sympycore/arithmetic/src/integer_utils.c']
                        )

if __name__ == '__main__':
    from distutils.core import setup
    setup(name='sympycore',
          version='0.1',
          package_dir = {'sympycore': 'sympycore'},
          ext_modules = [c_sexpr_ext,
                         c_iutils_ext]
          )

