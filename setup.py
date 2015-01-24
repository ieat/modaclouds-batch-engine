# -*- coding: utf-8 -*-
"""
Copyright 2014 Universitatea de Vest din Timișoara

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@info.uvt.ro>
@contact: marian@info.uvt.ro
@copyright: 2014 Universitatea de Vest din Timișoara
"""

import os
from setuptools import setup


def read(fname):
    if os.path.exists(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()


srcdir = 'src'
setup(
    name="batch-engine",
    version="0.0.1",
    author="Marian Neagul",
    author_email="marian@ieat.ro",
    description="Tool for handling batch schedulling software",
    license="APL",
    keywords="batch",
    url="http://www.modaclouds.eu/",
    package_dir={'': srcdir},
    #package_data={'': ['resources/*.yaml']},
    packages=["mbatch", ],
    long_description=read('README.md'),
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points={
        'console_scripts': [
            'batch-engine = mbatch.cli:main',
            'batch-engine-wrapper = mbatch.wrapper:main'
        ]
    },
    install_requires=["flask>=0.10", "flask-restful", "flask-restful-swagger"],
)
