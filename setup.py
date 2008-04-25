
CLASSIFIERS = """\
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
License :: OSI Approved
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

import os
if os.path.exists('MANIFEST'): os.remove('MANIFEST')
from distutils.core import Extension
expr_ext = Extension('sympycore.expr_ext',
                     sources = [os.path.join('src','expr_ext.c')],
                     )

if __name__ == '__main__':
    from distutils.core import setup
    setup(name='sympycore',
          version='0.2-svn',
          author = 'Pearu Peterson, Fredrik Johansson',
          author_email = 'sympycore@googlegroups.com',
          license = 'http://sympycore.googlecode.com/svn/trunk/LICENSE',
          url = 'http://sympycore.googlecode.com',
          download_url = 'http://code.google.com/p/sympycore/downloads/',
          classifiers=filter(None, CLASSIFIERS.split('\n')),
          description = 'SympyCore: an efficient pure Python Computer Algebra System',
          long_description = '''\
SympyCore project provides a pure Python package sympycore for
representing symbolic expressions using efficient data structures as
well as methods to manipulate them. Sympycore uses a clear algebra
oriented design that can be easily extended.
''',
          platforms = ["All"],
          packages = ['sympycore',
                      'sympycore.arithmetic',
                      'sympycore.arithmetic.mpmath',
                      'sympycore.basealgebra',
                      'sympycore.calculus',
                      'sympycore.calculus.functions',
                      'sympycore.functions',
                      'sympycore.logic',
                      'sympycore.matrices',
                      'sympycore.polynomials',
                      'sympycore.physics',
                      ],
          ext_modules = [expr_ext],
          package_dir = {'sympycore': 'sympycore'},
          )

