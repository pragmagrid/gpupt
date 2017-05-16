#!/opt/rocks/bin/python
#
#

from distutils.core import setup
import os

version = os.environ.get('ROCKS_VERSION')

# 
# main configuration of distutils
# 
setup(
    name = 'rocks-command-gpupt',
    version = version,
    description = 'Rocks GPU passthrough python library extension',
    author = 'Nadya Williams',
    author_email =  'nadya@sdsc.edu',
    maintainer = 'Nadya Williams',
    maintainer_email =  'nadya@sdsc.edu',
    platforms = ['linux'],
    url = 'http://www.rocksclusters.org',
    #main package, most of the code is inside here
    packages = [line.rstrip() for line in open('packages')],
    #data_files = [('etc', ['etc/rocksrc'])],
    package_data={'rocks.db.mappings': ['*.sql']},
    # disable zip installation
    zip_safe = False,
)
