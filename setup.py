from os.path import join
from setuptools import setup
import os
import sys

# validate python version
if sys.version_info < (3, 6):
  sys.exit('Sorry, ClipPlot requires Python 3.6 or later')

# populate list of all paths in `./clipplot/web`
web = []
dirs = [join('clipplot', 'web'), join('clipplot', 'models')]
for i in dirs:
  for root, subdirs, files in os.walk(i):
    if not files:
      continue
    for file in files:
      web.append(join(root.replace('clipplot/', '')
                          .replace('clipplot\\', ''), file))

setup(
  name='clipplot',
  version='0.0.2',
  packages=['clipplot'],
  package_data={
    'clip-plot': web,
  },
  keywords=['computer-vision',
            'webgl',
            'three.js',
            'machine-learning'],
  description='Visualize large image collections with WebGL',
  url='https://github.com/fr1ll/clip-plot',
  author='Forked from work by Douglas Duhaime',
  license='MIT',
  install_requires=[
    'cmake>=3.15.3',
    'Cython>=0.29.21',
    'glob2>=0.6',
    'h5py~=3.1.0',
    'iiif-downloader>=0.0.6',
    'numba>=0.53',
    'numpy>=1.19.5',
    'Pillow>=6.1.0',
    'pointgrid>=0.0.2',
    'python-dateutil>=2.8.0',
    'scikit-learn>=0.24.2',
    'scipy>=1.4.0',
    'six>=1.15.0',
    'tqdm>=4.61.1',
    'umap-learn>=0.5.1',
    'yale-dhlab-rasterfairy>=1.0.3',
    'matplotlib'
  ],
  entry_points={
    'console_scripts': [
      'clipplot=clipplot:parse',
    ],
  },
)
