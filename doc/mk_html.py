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

publish_file(source_path=path('userguide.rst'),
             destination_path=path('html','userguide.html'),
             writer_name='html')
