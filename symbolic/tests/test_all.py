"""
Run all tests found in test_*.py files.

Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""

import os
import imp
import glob

from numpy.testing import *

if __name__=='__main__':
    clstype = type(NumpyTestCase)
    i = 0
    for filename in glob.glob(os.path.join(os.path.dirname(__file__),'test_*.py')):
        name = os.path.splitext(os.path.basename(filename))[0]
        name0 = os.path.splitext(os.path.basename(__file__))[0]
        if name==name0: continue
        path = [os.path.dirname(filename)]
        file, pathname, description = imp.find_module(name, path)
        try:
            m = imp.load_module(name, file, pathname, description)
        finally:
            file.close()
        for n in dir(m):
            a = getattr(m,n)
            if isinstance(a,clstype) and issubclass(a,NumpyTestCase):
                i += 1
                s = '%s_%s = m.%s' % (n,i,n)
                exec s
    NumpyTest().run()
    #print Symbolic_namespace
