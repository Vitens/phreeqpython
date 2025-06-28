from setuptools import setup
import os
import sys
import zipfile
import urllib

setup(name='phreeqpython',
      version='1.5.5',
      description='Vitens viphreeqc wrapper and utilities',
      url='https://github.com/Vitens/phreeqpython',
      author='Abel Heinsbroek',
      author_email='abel.heinsbroek@vitens.nl',
      license='Apache Licence 2.0',
      packages=['phreeqpython'],
      include_package_data=True,
      package_data={'phreeqpython': ['phreeqpython/lib/*.so','phreeqpython/lib/*.dll','phreeqpython/lib/*.dylib', 'phreeqpython/database/*.dat'] },
      zip_safe=False,
      install_requires=['periodictable','numpy','scipy']
      )
