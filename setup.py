# -*- coding: utf-8 -*-
# (c) 2018-2021 The Hiveeyes Developers
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(name='saraswati',
      version='0.5.0',
      description='Saraswati - a robust, multi-channel audio recording, transmission and storage system',
      long_description=README,
      license="AGPL 3, EUPL 1.2",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Communications",
        "Topic :: Education",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Archiving",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Text Processing",
        "Topic :: Utilities",
      ],
      author='Andreas Motl',
      author_email='andreas@hiveeyes.org',
      url='https://github.com/hiveeyes/saraswati',
      keywords='audio multi-channel recording transmission storage robust',
      packages=find_packages(),
      include_package_data=True,
      package_data={
        'saraswati': [
            '*.default',
            '*.service',
        ],
      },
      zip_safe=False,
      test_suite='tests',
      install_requires=[
          "dataclasses; python_version<'3.7'",
          "importlib_metadata; python_version<'3.8'",
          "click>=7.1.2,<8",
          "cloup>=0.8.0,<0.9",
          "appdirs>=1.3,<2",
          "teetime>=0.0.3,<0.1",
      ],
      extras_require={
          "test": [
              "pytest>=4.6.7",
              "pytest-cov>=2.8.1",
              "PyGObject-stubs==0.0.2",
          ]
      },
      tests_require=[],
      entry_points={
          'console_scripts': [
              'saraswati = saraswati.cli:cli',
          ],
      },
)
