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

for n in ['usersguide', 'evaluation_rules', 'demo0_2',
          'structure', 'references']:
    publish_file(source_path=path(n+'.rst'),
                 destination_path=path('html',n+'.html'),
                 writer_name='html',
                 settings_overrides = dict(stylesheet_path=path('sympycore.css'),
                                           section_numbering=True),
                 )


publish_file(source_path=path('..','README.txt'),
             destination_path=path('html','README.html'),
             writer_name='html')
