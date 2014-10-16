#!/usr/bin/env python
# coding=utf-8

import sys
import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

version_string = '0.1.1'


# Defaults for py2app / cx_Freeze
default_build_options=dict(
    packages=[],
    )


setup(

    name='accuri2fcs',
    version=version_string,
    author='Martin Fitzpatrick',
    author_email='martin.fitzpatrick@gmail.com',
    url='https://github.com/mfitzp/accura2fcs',
    download_url='https://github.com/mfitzp/accura2fcs/zipball/master',
    description='Convert Accuri format flow cytometry files to standard .fcs',
    long_description='Accuri2fcs is a command line program for the conversion of accura .c6 \
        formatted flow cytometry files to standard .fcs. In practise this is relatively \
        straightforward as Accuri files are simply zip structures containing multiple .fcs. \
        in a structured format. However, extracting and naming these individual files is a \
        little more tricky. This program allows rapid batch processing of multiple Accura \
        files into multiple .fcs files, with regular expression sample name matching, splitting \
        and copying to build the output filenames. It can get quite complicated, see the examples. \
        ',
    packages = find_packages(),
    include_package_data = True,
    package_data = {
        '': ['*.txt', '*.rst', '*.md'],
    },
    exclude_package_data = { '': ['README.txt'] },

    entry_points = {
        'console_scripts': [
            'accuri2fcs = accuri2fcs.accuri2fcs:main',
        ],
    },

    install_requires = [],

    keywords='bioinformatics flow cytometry accuri facs research analysis science',
    license='BSD',
    classifiers=['Development Status :: 4 - Beta',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2',
               'License :: OSI Approved :: BSD License',
               'Topic :: Scientific/Engineering :: Bio-Informatics',
               'Topic :: Education',
               'Intended Audience :: Science/Research',
               'Intended Audience :: Education',
              ],
    )