#!/usr/bin/python3
from setuptools import setup, find_packages

setup(name='fackup',
      version='0.2.2',
      description='File backup tool using rsync and dar.',
      author='Benedykt Przybyło',
      author_email='b3niup@gmail.com',
      url='https://github.com/b3niup/fackup',
      keywords='backup dar rsync',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'fackup = fackup.core:main',
          ]
      },
      data_files=[('/etc', ['fackup.yml.example'])],
      install_requires=['PyYAML>=3.0'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.4',
          'Topic :: System :: Archiving :: Backup',
          'Topic :: System :: Systems Administration',
      ])
