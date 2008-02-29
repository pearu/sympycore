#!/usr/bin/env python

import os
root_dir = os.path.dirname(__file__)
path = lambda *paths: os.path.join(*((root_dir,)+paths))

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_file

for n in ['userguide', 'evaluation_rules', 'demo0_1']:
    publish_file(source_path=path(n+'.rst'),
                 destination_path=path('html',n+'.html'),
                 writer_name='html')


publish_file(source_path=path('..','README.txt'),
             destination_path=path('html','README.html'),
             writer_name='html')
