
#XXX: using numpy.distutils for colored output temporarily
from numpy.distutils.core import Extension
ext = Extension('pairs_ext',
                sources = ['pairsobject.c'],
                include_dirs = ['.']
                )

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(ext_modules = [ext])
