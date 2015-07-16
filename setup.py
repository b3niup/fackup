#!/usr/bin/python3
from setuptools import setup, find_packages

setup(name='fackup',
      version='0.1.0',
      description='File backup tool using rsync and dar.',
      author='Benedykt Przybyło',
      author_email='benedykt.przybylo@gmail.com',
      url='https://github.com/b3niup/fackup',
      packages=find_packages(),
      scripts=['scripts/fackup'],
      data_files=[('/etc', ['fackup.yml.example'])],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.4',
          'Topic :: System :: Systems Administration',
      ])

