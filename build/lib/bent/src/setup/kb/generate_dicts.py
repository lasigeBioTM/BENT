#!/usr/bin/env python

import bent.src.cfg as cfg
import orjson as json
import os
from bent.src.setup.kb.kb import KnowledgeBase

dict_dir = cfg.root_path + 'data/kbs/dicts/'


def generate_dicts_4_kb(kb=None, mode='reel', terms_filename=None, 
        edges_filename=None, kb_filename=None, input_format=None):
    
    out_dir = dict_dir + kb 

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    kb_obj = KnowledgeBase(kb, mode, terms_filename=terms_filename, 
        edges_filename=edges_filename, input_format=input_format)
    
    if mode == 'reel':
        name_to_id = json.dumps(kb_obj.name_to_id)
        
        with open(out_dir + '/name_to_id.json', 'wb') as outfile:
            outfile.write(name_to_id)
            outfile.close
        
        del name_to_id

        id_to_name = json.dumps(kb_obj.id_to_name)

        with open(out_dir + '/id_to_name.json', 'wb') as outfile2:
            outfile2.write(id_to_name)
            outfile2.close
        
        del id_to_name

        id_to_info = json.dumps(kb_obj.id_to_info)
        
        with open(out_dir + '/id_to_info.json', 'wb') as outfile3:
            outfile3.write(id_to_info)
            outfile3.close
        
        del id_to_info

        synonym_to_id = json.dumps(kb_obj.synonym_to_id)
        
        with open(out_dir + '/synonym_to_id.json', 'wb') as outfile4:
            outfile4.write(synonym_to_id)
            outfile4.close
        
        del synonym_to_id

        node_to_node = json.dumps(kb_obj.node_to_node)

        with open(out_dir + '/node_to_node.json', 'wb') as outfile5:
            outfile5.write(node_to_node)
            outfile5.close()
        
        del node_to_node

        if kb_obj.alt_id_to_id != None:
            alt_id_to_id = json.dumps(kb_obj.alt_id_to_id)
            
            with open(out_dir + '/alt_id_to_id.json', 'wb') as outfile6:
                outfile6.write(alt_id_to_id)
                outfile6.close

        #-------------------------------------------------------------------------
    
    elif mode == 'nilinker' and kb == 'chebi':
        
        id_to_name_nilinker = json.dumps(kb_obj.id_to_name)
        
        with open(out_dir + '/id_to_name_nilinker.json', 'wb') as outfile4:
            outfile4.write(id_to_name_nilinker)
            outfile4.close
        
        del id_to_name_nilinker

def generate(
        kbs=[], custom=False, kb_name=None, kb_filename=None, 
        terms_filename=None, edges_filename=None, input_format=None):
    
    #kbs = [
        #('medic', 'reel'), 
        #('ctd_chem', 'reel'), 
        #('go_bp', 'reel'), 
        #('go_cc', 'reel')
        #('ncbi_gene', 'reel'), 
        #('ncbi_taxon', 'reel'),
        #('ctd_gene', 'reel'),
        #('chebi', 'reel'), 
        #('chebi', 'nilinker')
        #('do', 'reel'), 
        #('ctd_anat', 'reel'), 
        #('cellosaurus', 'reel'), 
        #('cl', 'reel'),
        #('uberon', 'reel'),
    #    ]    
    
    if custom:

        if edges_filename != None and terms_filename != None:
            generate_dicts_4_kb(kb=kb_name, terms_filename=terms_filename, 
                edges_filename=edges_filename, input_format=input_format)

        else:
            if kb_filename != None:
                generate_dicts_4_kb(kb=kb_name, kb_filename=kb_filename, 
                    input_format=input_format)

            else:
                raise ValueError('It is necessary to either define a terms \
                    filename and an edges filename OR a knowledge base filename')
    
    else:
        for pair in kbs:
            print('Generating KB dicts for:', pair)
            generate_dicts_4_kb(kb=pair[0], mode=pair[1])

        