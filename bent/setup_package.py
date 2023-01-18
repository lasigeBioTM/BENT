#!/usr/bin/env python

import bent.src.cfg as cfg
import os
import subprocess


def setup_package():

    #-------------------------------------------------------------------------
    #                      Install missing dependencies
    #-------------------------------------------------------------------------
    cwd = os.getcwd()
    scripts_path = cfg.root_path + 'scripts/'
    os.chdir(scripts_path)
    os.chmod('setup_package.sh', 0o755)
    subprocess.call(scripts_path + 'setup_package.sh')

    #-------------------------------------------------------------------------
    #                      Download data
    #-------------------------------------------------------------------------
    os.chmod('get_data.sh', 0o755)
    subprocess.call(scripts_path + 'get_data.sh')
    os.chdir(cwd)