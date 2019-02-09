#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

# The only thing you have to do is to
# rewrite meta-data in __meta__.py as these default value below
# and write this module_name
MODULE_NAME = 'alarmclock'
# Personal namespace package
NAMESPACE = 'sine'
DESCRIPTION = 'package description'
URL = 'https://github.com/SineObama/'
EMAIL = '714186139@qq.com'
AUTHOR = 'Xian Zheng'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.0.1'
REQUIRED = [
    # What packages are required for this module to be executed?
    # 'requests', 'maya', 'records',
]
# If you do change the License, remember to change the Trove Classifier for that!
LICENSE='MIT'
CLASSIFIERS=[
    # Trove classifiers
    # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy'
]

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Replace globals with value in __meta__.py
# Load the package's __meta__.py module as a dictionary.
NAME = NAMESPACE + '.' + MODULE_NAME
here = os.path.abspath(os.path.dirname(__file__))
meta = {}
with open(os.path.join(here, NAMESPACE, MODULE_NAME, '__meta__.py')) as f:
    exec(f.read(), meta)
for key, value in meta.items():
    exec(key + ' = meta[\'' + key + '\']')

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = '\n' + f.read()

class MyCommand(Command):
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('>>>>{0}'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

class UploadCommand(MyCommand):
    """Support setup.py upload."""

    description = 'Build and publish the package.'

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source distribution...')
        os.system('{0} setup.py sdist'.format(sys.executable))

        # self.status('Building executable installer for MS Windows...')
        # os.system('{0} setup.py bdist_wininst'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine...')
        os.system('twine upload dist/*')

        self.status('Pushing git tags...')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')
        
        sys.exit()

class ReinstallCommand(MyCommand):
    """repack the package and reinstall locally."""
    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'build'))
        except OSError:
            pass

        self.status('Building...')
        os.system('{0} setup.py build'.format(sys.executable))

        self.status('Installing...')
        os.system('{0} setup.py install'.format(sys.executable))
        
        sys.exit()

class UninstallCommand(MyCommand):
    def run(self):
        self.status('Uninstalling the package locally')
        os.system('pip uninstall ' + NAME)
        
        sys.exit()

# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    namespace_packages=[NAMESPACE],
    install_requires=REQUIRED,
    include_package_data=True,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
        'rei': ReinstallCommand,
        'uni': UninstallCommand,
    },
)
