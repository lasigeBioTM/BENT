#!/usr/bin/env python

import bent.src.cfg as cfg
import os
import subprocess


def setup_package(target_kbs, only_kb_dicts=False):

    cwd = os.getcwd()

    scripts_path = cfg.root_path + 'scripts/'
    os.chdir(scripts_path)

    data_dir = '../data'

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    
    if only_kb_dicts == False:
        os.chmod('setup_package.sh', 0o755)
        subprocess.call(scripts_path + 'setup_package.sh')

        #----------------------------------------------------------------------
        #         Download NILINKER, relations and entity frequency data
        #----------------------------------------------------------------------
        os.chmod('get_data.sh', 0o755)
        subprocess.call(scripts_path + 'get_data.sh')

    
    #-------------------------------------------------------------------------
    #                           Download kb dicts
    #-------------------------------------------------------------------------
    
    os.chmod('get_kb_dicts.sh', 0o755)
    
    kb_dicts_dir = cfg.root_path + 'data/kbs/'
    
    if not os.path.exists(kb_dicts_dir):
        os.mkdir(kb_dicts_dir) 

    kb_dicts_dir = cfg.root_path + 'data/kbs/dicts/'
    
    if not os.path.exists(kb_dicts_dir):
        os.mkdir(kb_dicts_dir) 

    kb_script = scripts_path + 'get_kb_dicts.sh'

    if target_kbs == ['all']:
        
        available_kbs = ['medic', 'do', 'chebi', 'ctd_chem', 'ncbi_gene', 
            'ctd_gene', 'ctd_anat', 'uberon', 'go_bp', 'ncbi_taxon', 'go_cc',
            'cell_ontology', 'cellosaurus']

        for kb in available_kbs:

            # check if file is already downloaded
            if kb in os.listdir(kb_dicts_dir):
                print(kb, 'already downloaded!')
            
            else:  
                subprocess.call([kb_script, kb])

    else:

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