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

publish_file(source_path=path('usersguide_latex.rst'),
             destination_path=path('sympycore_usersguide.tex'),
             writer_name='latex',
             settings_overrides = dict(documentoptions='12pt,a4paper',
                                       use_latex_toc=True,
                                       use_verbatim_when_possible=True,
                                       )
             )

os.chdir(path())
s = os.system('pdflatex sympycore_usersguide.tex')
if not s:
    s = os.system('pdflatex sympycore_usersguide.tex')
    for e in ['aux','log','out','tex', 'toc']:
        os.system('rm sympycore_usersguide.%s' % e)
