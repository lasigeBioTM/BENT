#!/usr/bin/env python

import bent.src.cfg as cfg
import os
import subprocess


def get_additional_kbs(target_kbs):

    cwd = os.getcwd()
    os.chdir(cfg.root_path)
    
    #-------------------------------------------------------------------------
    #                           Download kb dicts
    #-------------------------------------------------------------------------
    
    os.chmod('get_kb_dicts.sh', 0o755)
    
    kb_dicts_dir = cfg.root_path + '/data/kbs/dicts/'
    kb_script = cfg.root_path + '/get_kb_dicts.sh'

    if len(target_kbs) >= 1:
        
        for kb in target_kbs:

            # check if file is already downloaded
            if kb in os.listdir(kb_dicts_dir):
                print(kb, 'already downloaded!')
                
            else:
                subprocess.call([kb_script, kb])

    else:
        raise ValueError(
            'You need to specify at least one target knowledge base!')

    os.chdir(cwd)
