from setuptools import setup  # Always prefer setuptools over distutils
import spartan.__info__ as spartan

setup(
   name = 'spartan',
   version = spartan.__version__,
   author = spartan.__author__,
   author_email = spartan.__email__,
   packages = ['spartan'],
   entry_points = {'gui_scripts': ['spartan = spartan.__main__:main',],},
   url = spartan.__website__,
   license = spartan.__license__,
   description = 'Python tool for easy data plotting',
   python_requires = '>=3.6',
   install_requires = [
      "PyQt5 >= v5.10.1",
      "npyscreen >= 4.10.5",
      "scipy >= 1.0.1",
      "numpy >=1.14.2",
      "h5py >= 2.8.0",
      "tqdm >= 4.23.4",
      "astropy >= 3.0.2",
      "matplotlib >= 2.2.2",
   ],
   include_package_data=True,
)
