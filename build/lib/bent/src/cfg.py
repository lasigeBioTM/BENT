#!/usr/bin/env python
import os

# The root path for the CONDA project installation
#root_path = str(os.path.dirname(bent.__file__)).replace('lib/python3.7/site-packages/bota', '')
root_path = os.environ["CONDA_PREFIX"] + '/'

data_dir = '{}data/'.format(root_path)

tmp_dir = '.tmp/'