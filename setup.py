import os
from setuptools import setup
file_path = os.path.dirname(os.path.realpath(__file__))

try:
    version = os.environ['ZAC_VERSION']
except:
    version_file = open(os.path.join(file_path, 'zac/VERSION'), 'rb')
    version = version_file.read().decode().strip()

with open('README.md') as f:
    readme = f.read()

setup(name                          = 'zac',
      version                       = version,
      description                   = 'Ziya Atmospheric Correction (ZAC)',
      long_description              = readme,
      long_description_content_type ='text/markdown',
      author                       = 'Tang Ziya',
      author_email                 = 'tcztzy@gmail.com',
      classifiers                  = ['Development Status :: 4 - Beta',
                                      'Programming Language :: Python :: 3'],
      install_requires             = ['gdal>=2.1', 'numpy>=1.13', 'scipy>=1.0', 'psutil','six', 'numba',
                                      'lightgbm>=2.1.0','requests', 'scikit-learn', 'scikit-image', 'pyproj'],
      url                          = 'https://github.com/tcztzy/zac',
      license                      = "GNU Affero General Public License v3.0",
      include_package_data         = True,
      packages                     = ['zac'],
     )
