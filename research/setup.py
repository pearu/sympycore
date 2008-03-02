
#XXX: using numpy.distutils for colored output temporarily
from numpy.distutils.core import Extension
ext = Extension('noddy2',
                sources = ['noddy.c'],
                include_dirs = ['.']
                )
ext5 = Extension('noddy5',
                sources = ['noddy5.c'],
                include_dirs = ['.']
                )

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(ext_modules = [ext, ext5])
