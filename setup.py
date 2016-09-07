from setuptools import setup
import sys
import zipfile
import urllib
from setuptools.command.develop import develop
from setuptools.command.install import install

def fetch_viphreeqc():
    print "Fetching latest VIPhreeqc build from ci..."
    from_zip = False
    if sys.platform == "darwin":
        dll_name = "viphreeqc.dylib"
    elif sys.platform == "linux2":
        dll_name = "viphreeqc.so"
    else:
        dll_name = "viphreeqc.zip"

    urllib.urlretrieve("http://ci.abelheinsbroek.nl/"+dll_name, "phreeqpython/lib/"+dll_name)

    if dll_name == "viphreeqc.zip":
        print "Unpacking library"
        with zipfile.ZipFile("phreeqpython/lib/"+dll_name,"r") as archive:
            archive.extractall("phreeqpython/lib")
        os.remove("phreeqpython/lib/viphreeqc.zip")


    print "Done!"
    

class PostDevelopCommand(develop):
    def run(self):
        fetch_viphreeqc()
        develop.run(self)

class PostInstallCommand(install):
    def run(self):
        fetch_viphreeqc()
        install.run(self)

setup(name='phreeqpython',
      version='0.2',
      description='Vitens viphreeqc wrapper and utilities',
      url='https://github.com/VitensTC/phreeqpython',
      author='Abel Heinsbroek',
      author_email='abel.heinsbroek@vitens.nl',
      license='Apache Licence 2.0',
      packages=['phreeqpython'],
      zip_safe=False,
      cmdclass={
          'develop': PostDevelopCommand,
          'install': PostInstallCommand
          })
