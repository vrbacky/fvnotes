#!/usr/bin/env python3
'''FVnotes setup'''

import codecs
import os
import re
import sys

NAME = 'FVnotes'

try:
    from pip.req import parse_requirements
except ImportError:
    raise RuntimeError(
        'Please install pip before installing {}.\n'.format(NAME))
try:
    from setuptools import setup, find_packages
except ImportError:
    raise RuntimeError('Python package setuptools hasn\'t been installed.\n'
                       'Please install setuptools before installing '
                       '{}.\n'.format(NAME))
if sys.version_info < (3, 6, 0):
    raise RuntimeError('Python 3.6.0 or higher required.\n')


def read(*parts):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(current_dir, *parts), "r").read()


def get_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^VERSION = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def get_long_description():
    try:
        with open('README.rst', 'r') as readme_file:
            return readme_file.read()
    except IOError:
        print('Cannot find README.rst file. Long description will be empty.\n')
        return ''


def get_requirements():
    requirements_file = 'requirements.txt'
    try:
        requirements = parse_requirements(requirements_file, session=False)
    except TypeError:
        requirements = parse_requirements(requirements_file)
    return [str(r.req) for r in requirements]


def get_scripts():
    scripts = (
        'fvnotes',
    )
    return [os.path.join('bin', i) for i in scripts]


setup(name=NAME,
      version=get_version(NAME.lower(), '__init__.py'),
      description='The open source plain-text editor and notes manager',
      long_description=get_long_description(),
      install_requires=get_requirements(),
      keywords='notes journal',
      url='https://github.com/vrbacky/fvnotes',
      author='Filip Vrbacky',
      author_email='vrbacky@fnhk.cz',
      maintainer='Filip Vrbacky',
      maintainer_email='vrbacky@fnhk.cz',
      license=('GPLv3'),
      zip_safe=False,
      packages=find_packages(exclude=['bin', 'docs', 'test']),
      scripts=get_scripts(),
      test_suite='test',
      include_package_data=True,
      data_files=[
          'fvnotes/gui/icons/new_note.png',
      ],
      classifiers=(
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Natural Language :: English',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Topic :: Office/Business :: News/Diary',
          )
      )
