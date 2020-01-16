from setuptools import setup
import os
import sys
import zipfile
import urllib
from setuptools.command.develop import develop
from setuptools.command.install import install

if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve


def fetch_viphreeqc():
    print("Fetching latest VIPhreeqc build from ci...")
    from_zip = False
    if sys.platform == "darwin":
        dll_name = "viphreeqc.dylib"
    elif "linux" in sys.platform:
        dll_name = "viphreeqc.so"
    else:
        dll_name = "viphreeqc.zip"

    
    dll_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "phreeqpython" + os.sep + "lib" + os.sep +dll_name
    print("Downloading to:", dll_path)

    urlretrieve("http://ci.abelheinsbroek.nl/"+dll_name, dll_path)

    if dll_name == "viphreeqc.zip":
        with zipfile.ZipFile(dll_path,"r") as archive:
            extract_path = os.path.dirname(os.path.abspath(__file__)) + "\phreeqpython\lib"
            print("Unpacking library to:", extract_path)
            archive.extractall(extract_path)
        os.remove(dll_path)


    print("Done!")
    

class PostDevelopCommand(develop):
    def run(self):
        fetch_viphreeqc()
        develop.run(self)

class PostInstallCommand(install):
    def run(self):
        fetch_viphreeqc()
        install.run(self)

setup(name='phreeqpython',
      version='1.3.2',
      description='Vitens viphreeqc wrapper and utilities',
      url='https://github.com/Vitens/phreeqpython',
      author='Abel Heinsbroek',
      author_email='abel.heinsbroek@vitens.nl',
      license='Apache Licence 2.0',
      packages=['phreeqpython'],
      include_package_data=True,
      zip_safe=False,
      cmdclass={
          'develop': PostDevelopCommand,
          'install': PostInstallCommand
          },
      install_requires=['periodictable']
      )
