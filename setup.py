# -*- coding: utf-8 -*-

"""A setuptools based setup module.

For more information, please see
- https://pypi.python.org/pypi/setuptools
- https://pythonhosted.org/setuptools
- https://python-packaging-user-guide.readthedocs.io/en/latest/distributing/
- https://packaging.python.org/en/latest/distributing.html
- https://github.com/pypa/sampleproject

"""

import os
import setuptools
import sys

from src import bots  # @UnresolvedImport


def read(*names, **kwargs):
    """Return the contents of a file.

    Default encoding is UTF-8, unless specified otherwise.

    Args:
        - names (list, required): list of strings, parts of the path.
          the path might be relative to the current file.

    Keyword Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
      String containing the content of the file.

    Examples:
        >>> read('docs/readme.rst')
            u'Overview\n--------\n...'

        >>> read('docs', 'readme.rst')
            u'Overview\n--------\n...'

    """
    fn = os.path.join(os.path.dirname(__file__), *names)
    with open(fn, encoding=kwargs.get('encoding', 'utf8')) as fd:
        return fd.read()


classifiers = [
    'Development Status :: 4 - Beta',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Framework :: Django :: 1.8',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Topic :: Office/Business',
    'Topic :: Office/Business :: Financial',
    'Topic :: Other/Nonlisted Topic',
    'Topic :: Communications',
    'Environment :: Console',
    'Environment :: Web Environment',
]

install_requires = [
    'Django~=1.8.8',
    'Cherrypy>3.1.0,<9.0',
    'setuptools',
]

extras_require = {
    'docs': [
        'sphinx',
        'sphinx_rtd_theme',
    ],
    'mysql': ['PyMySQL'],
    'postgres': ['psycopg2'],
    'tools': [
        'ecdsa',     # dep of paramiko
        'Genshi',    # for using templates/mapping to HTML)
        'paramiko',  # SFTP
        'pdfminer',  # parse pdf-files
        'xlrd',      # parse excel-files
    ],
}

scripts = [
    'scripts/bots-dirmonitor.py',
    'scripts/bots-engine.py',
    'scripts/bots-grammarcheck.py',
    'scripts/bots-job2queue.py',
    'scripts/bots-jobqueueserver.py',
    'scripts/bots-plugoutindex.py',
    'scripts/bots-updatedb.py',
    'scripts/bots-webserver.py',
    'scripts/bots-xml2botsgrammar.py',
]

entry_points = {
    'console_scripts': [
        'bots-dirmonitor = bots.dirmonitor:start',
        'bots-engine = bots.engine:start',
        'bots-grammarcheck = bots.grammarcheck:start',
        'bots-job2queue = bots.job2queue:start',
        'bots-jobqueueserver = bots.jobqueueserver:start',
        'bots-plugoutindex = bots.plugoutindex:start',
        'bots-updatedb = bots.updatedb:start',
        'bots-webserver = bots.webserver:start',
        'bots-xml2botsgrammar = bots.xml2botsgrammar:start',
    ]
}

# Add OS-specific dependencies.
if sys.platform == 'win32':
    install_requires.append('pywin32')
else:
    install_requires.append('pyinotify')

kwargs = {
    'name':                 'django-bots',
    'version':              bots.__version__,
    'author':               'hjebbers',
    'author_email':         'hjebbers@gmail.com',
    'maintainer':           'Lane Shaw',
    'maintainer_email':     'lshaw.tech@gmail.com',
    'url':                  'https://github.com/edi-enthusiasts/django-bots',
    'description':          'Bots open source edi translator',
    'long_description':     'Bots is complete software for edi (Electronic Data Interchange): translate and communicate. All major edi data formats are supported: edifact, x12, tradacoms, xml',
    'platforms':            'OS Independent (Written in an interpreted language)',
    'license':              'GNU General Public License (GPL)',
    'keywords':             'edi edifact x12 tradacoms xml fixedfile csv',
    'packages':             setuptools.find_packages('src'),
    'package_dir':          {'': 'src'},
    'include_package_data': True,
    'zip_safe':             False,
    'classifiers':          classifiers,
    'install_requires':     install_requires,
    'extras_require':       extras_require,
    'scripts':              scripts,
    'entry_points':         entry_points,
}

if __name__ == '__main__':
    setuptools.setup(**kwargs)
