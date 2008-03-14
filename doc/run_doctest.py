
import os
import sys

root_dir = os.path.abspath(os.path.dirname(__file__))
path = lambda *paths: os.path.abspath(os.path.join(*((root_dir,)+paths)))

sys.path.insert(0, path('..'))

import doctest
doctest.testfile(path("usersguide_content.rst"), module_relative=False)
doctest.testfile(path("demo0_2.rst"), module_relative=False)
doctest.testfile(path('..',"README.txt"), module_relative=False)
