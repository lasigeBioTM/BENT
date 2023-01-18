#!/usr/bin/env python

import bent.src.cfg as cfg
import os
import random
import string
from bent.src.REEL.pre_process import pre_process
from bent.src.REEL.post_process import process_results


def run(ner_dir, kb, entity_type, abbreviations):
    """Apply the REEL model (preprocess, candidate scoring with PPR, 
    postprocess) to the entities present in files in ner_dir.

    :param ner_dir: path to directory where the recognized entities are
        stored in the annotations files
    :type ner_dir: str
    :param kb: target knowledge base
    :type kb: str
    :param entity_type: the type of the entities that will be linked
    :type entity_type: str
    :param abbreviations: abbreviations with format: 
        {'doc_id': {'abbv1': 'long_form'}]
    :type abbreviations: dict
    :return: nel_run_id representing the identifier of the current run of REEL.
        The results of the run will be located in the directory 
        'tmp/REEL/results/<run_id/>'.
    :rtype: str
    """

    nel_run_id = ''.join(random.choices(string.ascii_uppercase + string.digits, 
        k=15))
    nel_run_name = nel_run_id + '_' + entity_type

    # Use relations extracted from external corpora and relations described in 
    # the targer knowledge base
    link_mode='kb_corpus' 

    # Use NILINKER model if available
    nil_mode = 'none'
    available_kbs_nilinker = [
        'chebi', 'ctd_chem', 'medic', 'go_bp', 'hp']

    if kb in available_kbs_nilinker:
        nil_mode = 'NILINKER'
    #-------------------------------------------------------------------------#
    #                        REEL: PRE_PROCESSING                             
    #        Pre-processes the corpus to create a candidates file for each     
    #        document in dataset to allow further building of the              
    #        disambiguation graph.                                             
    #-------------------------------------------------------------------------#
    pre_process(nel_run_name, ner_dir, kb, entity_type, link_mode, nil_mode, 
        abbreviations)
   
    #------------------------------------------------------------------------#
    #                          REEL: PPR                                     
    #         Builds a disambiguation graph from each candidates file:            
    #         the nodes are the candidates and relations are added                
    #         according to candidate link_mode. After the disambiguation          
    #         graph is built, it runs the PPR algorithm over the graph            
    #         and ranks each candidate.                                           
    #------------------------------------------------------------------------#
    if kb != 'ncbi_gene':
        ppr_filepath = '{}scripts/'.format(cfg.root_path)
        comm = 'java -classpath :{} ppr_for_ned_all {} ppr_ic'.\
            format(ppr_filepath, nel_run_name)
        os.system(comm)

    #------------------------------------------------------------------------#
    #                         REEL: Post-processing                                                                      
    #------------------------------------------------------------------------# 
    process_results(nel_run_name, entity_type, kb)
    
    return nel_run_name