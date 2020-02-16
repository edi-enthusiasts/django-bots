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


version = '3.3.0-rc0'

classifiers = [
    'Development Status :: 4 - Beta',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
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
    'setuptools'
]

extras_require = {
    'docs': [
        'sphinx',
        'sphinx_rtd_theme'
    ],
    'tools': [
        'ecdsa',     # dep of paramiko
        'Genshi',    # for using templates/mapping to HTML)
        'paramiko',  # SFTP
        'pdfminer',  # parse pdf-files
        'pycrypto',  # SFTP
        'xlrd'       # parse excel-files
    ]
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
    'scripts/bots-xml2botsgrammar.py'
]

# Add OS-specific dependencies.
if sys.platform == 'win32':
    install_requires.append('pywin32')
else:
    install_requires.append('pyinotify')

kwargs = {
    'name':                 'edi-bots-server',
    'version':              version,
    'author':               'hjebbers',
    'author_email':         'hjebbers@gmail.com',
    'maintainer':           'Lane Shaw',
    'maintainer_email':     'lshaw.tech@gmail.com',
    'url':                  'https://github.com/edi-enthusiasts/edi-bots-server',
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
    'scripts':              scripts
}

setuptools.setup(**kwargs)
