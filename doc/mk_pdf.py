#!/usr/bin/env python

import os
import commands
root_dir = os.path.dirname(__file__)
path = lambda *paths: os.path.join(*((root_dir,)+paths))

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_file

publish_file(source_path=path('userguide.rst'),
             destination_path=path('sympycore_userguide.tex'),
             writer_name='latex')

os.chdir(path())
s = os.system('pdflatex sympycore_userguide.tex')
if not s:
    for e in ['aux','log','out','tex']:
        os.system('rm sympycore_userguide.%s' % e)
