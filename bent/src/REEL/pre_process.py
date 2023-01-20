#!/usr/bin/env python

import bent.src.cfg as cfg
import orjson as json
import os
import sys
from bent.src.REEL.candidates import write_candidates_file, generate_candidates_list
from bent.src.REEL.information_content import generate_ic_file
from bent.src.NILINKER.predict_nilinker import load_model
from bent.src.REEL.utils import entity_string, check_if_candidates_dir
from bent.src.utils import garbage_collect

sys.path.append("./")


def build_entity_candidate_dict(
        ner_dir, candidates_dir, kb, id_to_info, name_to_id, synonym_to_id, 
        kb_edges, link_mode, extracted_relations, kb_cache, entity_type, 
        abbreviations, min_match_score, nil_model_name='none', nilinker=None):
    """Build a dictionary including the candidates for all entity mentions in 
        all the input documents.

    :param ner_dir: path to directory where the recognized entities are
        stored in the annotations files
    :type ner_dir: str
    :param kb: target knowledge base
    :type kb: str
    :param id_to_info: mappings between KB identifiers and information
    :type id_to_info: dict
    :param name_to_id: mappings between each kb concept name and 
        the respective id
    :type name_to_id: dict
    :param synonym_to_id: mappings between each synonym for a given kb concept 
        and the respective id
    :type synonym_to_id: dict
    :param kb_cache: candidates cache for the given kb
    :type kb_cache: dict
    :param entity_type: the type of the entities that will be linked
    :type entity_type: str
    :param abbreviations: abbreviations with format 
        {'doc_id'':' {'abbv1': 'long_form'}]
    :type abbreviations: dict
    :param min_match_score: minimum lexical similarity between entity text and 
        candidate text-exclude candidates with a lexical similarity below 
        min_match_score
    :type min_match_score: float
    :param nil_mode: model to deal with the NIL entities ('none' or 'NILINKER)
    :type nil_mode: str
    :param nilinker: the loaded NILINKER model if 'nil_mode'='NILINKER, 
        defaults to None
    :type nilinker: _type_, optional

    :return: entities_candidates (dict) with format 
        {doc_id':' {mention:[candidate1, ...]} }, changed_cache_final (bool) 
        indicating wether the candidates cache has been updated comparing with
        preivous execution of the script, and kb_cache_up (dict), which 
        corresponds to the candidates cache for given KB, updated or not 
        according to the value of changed_cache
    :rtype: tuple with dict, bool, dict
    """
    
    doc_count = 0
    changed_cache_final = False
    kb_cache_up = None
    names = set(name_to_id.keys())
    synonyms = set(synonym_to_id.keys())

    ner_out_docs = os.listdir(ner_dir)
    
    for doc in ner_out_docs:
        ner_annots = None
        doc_id = doc.strip('.ann')

        with open(ner_dir + doc, 'r') as ner_doc:
            ner_annots = ner_doc.readlines()
            ner_doc.close()
        
        doc_count += 1 
        check_entity = []
        doc_entities_final = []
        doc_abbrvs = {}
        
        if doc_id in abbreviations:
            doc_abbrvs = abbreviations[doc_id]

        kb_id_2_id = {}
        
        for line in ner_annots:
            annot_type = ''
            entity_text = ''

            if line != '\n':
                line_data = line.split('\t')
                annot_type = line_data[1].split(' ')[0]
                entity_text = line_data[2].strip('\n')
            
            if annot_type.lower() == entity_type.lower() \
                    and entity_text not in check_entity:
                # Only disambiguate entities belonging to the same given
                # entity type
                # Repeated instances of the same entity in a document 
                # are not considered
                check_entity.append(entity_text)
                
                # Get candidates list for entity
                candidates_list, \
                    changed_cache, \
                    kb_cache_up, \
                    kb_id_2_id = generate_candidates_list(
                                                    entity_text, 
                                                    kb, 
                                                    id_to_info, 
                                                    names,
                                                    synonyms,
                                                    name_to_id, 
                                                    synonym_to_id,  
                                                    kb_cache,  
                                                    min_match_score,
                                                    doc_abbrvs,
                                                    kb_id_2_id)
                
                if changed_cache:
                    #There is at least 1 change in the cache file
                    changed_cache_final = True

                if len(candidates_list) == 0: 
                    
                    if nil_model_name != 'none':
                        # The model will try to disambiguate the NIL entity
                        top_candidates_up = []

                        if nil_model_name == 'NILINKER':
                            # Find top-k candidates with NILINKER and include
                            # them in the candidates file
                            top_candidates = nilinker.prediction(
                                                entity_text)
                                    
                        for cand in top_candidates:
                            kb_id = cand[0]

                            if nil_model_name == 'NILINKER':
                                kb_id = cand[0].replace(":", "_")
                        
                            cand_up = {'kb_id': kb_id , 
                                        'name': cand[1],
                                        'match_score': 1.0}
                            
                            top_candidates_up.append(cand_up)
                        
                        candidates_list, \
                            changed_cache, \
                            kb_cache_up, \
                            kb_id_2_id = generate_candidates_list(
                                            entity_text, 
                                            kb, 
                                            id_to_info, 
                                            names, 
                                            synonyms,
                                            name_to_id, 
                                            synonym_to_id, 
                                            kb_cache, 
                                            min_match_score, 
                                            doc_abbrvs, 
                                            kb_id_2_id,
                                            nil_candidates=top_candidates_up)
                    
                    elif nil_model_name == 'none':
                        # Since nil entities are not disambiguated,
                        # create a dummy candidate
                        candidates_list = [
                            {'url': 'NIL', 
                            'name': 'none', 
                            'outcount': 0, 
                            'incount': 0, 
                            'id': -1, 'links': [], 
                            'score': 0}]
                        
                entity_str = entity_string.format(
                    entity_text, entity_text.lower(), entity_type, 
                    doc_count, doc_id, 'unknown')
                
                add_entity = [entity_str, candidates_list]

                doc_entities_final.append(add_entity)

                del candidates_list

        if doc_entities_final != []:
            #In this document there is at least 1 entity
            #------------------------------------------------------------------
            #                        Generate candidates files
            #------------------------------------------------------------------
            write_candidates_file(
                kb, doc_entities_final, candidates_dir, entity_type, kb_edges, 
                link_mode, extracted_relations, doc_id)
        
        del doc_abbrvs
        del doc_entities_final
        del kb_id_2_id
     
    del names
    del synonyms
   
    return changed_cache_final, kb_cache_up
    

def pre_process(
        run_id, ner_dir, kb, entity_type, link_mode, nil_mode, abbreviations):
    """Execute all pre-processing steps that are necessary to create the 
        candidate files, which will be the input for the PPR algorithm. The 
        candidate files will be located in the directory 
        'tmp/REEL/candidates/<run_id>'.

    :param run_id: representing the identifier of the current run of REEL
    :type run_id: str
    :param ner_dir: path to directory where the recognized entities are
        stored in the annotations files
    :type ner_dir: str
    :param kb: target knowledge base
    :type kb: str
    :param entity_type: the type of the entities that will be linked
    :type entity_type: str
    :param link_mode: specifies the way the edges are built in the 
        disambiguation graphs that are the input of the PPR algorithm 
        ('corpus' - extracted relations from an external corpus, 
        'kb' - relations described in the knowledge base, 
        'kb_corpus' - extracted relations from an external corpus and relations
        described in the knowledge base, 
    :type link_mode: str
    :param nil_mode: model to deal with the NIL entities ('none' or 'NILINKER)
    :type nil_mode: str
    param abbreviations: abbreviations with format: 
        {'doc_id': {'abbv1': 'long_form'}]
    :type abbreviations: dict
    """

    #-------------------------------------------------------------------------
    #                          Create directories
    #-------------------------------------------------------------------------
    if not os.path.exists(cfg.tmp_dir):
        os.mkdir(cfg.tmp_dir)

    if not os.path.exists(cfg.tmp_dir + run_id):
        os.mkdir(cfg.tmp_dir + run_id)

    if not os.path.exists(cfg.tmp_dir + 'REEL/'):
        os.mkdir(cfg.tmp_dir + 'REEL/')

    if not os.path.exists(cfg.tmp_dir + 'REEL/cache/'):
        os.mkdir(cfg.tmp_dir + 'REEL/cache/')

    os.mkdir('{}{}/REEL/'.format(cfg.tmp_dir, run_id))
    os.mkdir('{}{}/REEL/candidates'.format(cfg.tmp_dir, run_id))
    os.mkdir('{}{}/REEL/results/'.format(cfg.tmp_dir, run_id))
    
    #-------------------------------------------------------------------------
    #                            Import KB info
    #-------------------------------------------------------------------------

    # Load preprocessed dicts
    name_to_id = {}
    synonym_to_id = {}
    kb_dicts_dir = '{}data/dicts/{}/'.format(cfg.root_path, kb) 
    
    with open(kb_dicts_dir + 'name_to_id.json', 'r') as dict_file:
        name_to_id = json.loads(dict_file.read())
        dict_file.close()

    synonyms_filepath = kb_dicts_dir + 'synonym_to_id_full.json'

    if 'synonym_to_id_full.json' not in os.listdir(kb_dicts_dir):
        synonyms_filepath = kb_dicts_dir + 'synonym_to_id.json'
    
    with open(synonyms_filepath, 'r') as dict_file2:
        synonym_to_id = json.loads(dict_file2.read())
        dict_file2.close()    

    id_to_info = None
    
    if kb != 'ncbi_gene':
        id_to_info_filepath = kb_dicts_dir + 'id_to_info.json'

        with open(id_to_info_filepath, 'r') as dict_file3:
            id_to_info = json.loads(dict_file3.read())
            dict_file3.close()  

    #-------------------------------------------------------------------------
    #                  Import cache file (if available)
    #-------------------------------------------------------------------------
    kb_cache_filename = '{}/REEL/cache/{}.json'.format(cfg.tmp_dir, kb)
    kb_cache = {}

    if os.path.exists(kb_cache_filename):
        cache_file = open(kb_cache_filename, 'r')
        kb_cache = json.loads(cache_file.read())
        cache_file.close()

    changed_cache_final = False
    
    #-------------------------------------------------------------------------
    #                            Load NILINKER
    #-------------------------------------------------------------------------
    if nil_mode == 'NILINKER':
        # Prepare NILINKER and get compiled model ready to predict
        # top_k defines the number of candidates that NILINKER wil return
        # for each given entity
        top_k = 1
        nilinker = load_model(kb, top_k=int(top_k))
      
    else:
        nilinker = None
    
    #-------------------------------------------------------------------------
    #            Import relations to add to the disambiguation graphs
    #-------------------------------------------------------------------------
    extracted_relations = {}
    
    if link_mode == 'corpus' or link_mode == 'kb_corpus': 
        relations_dir = '{}data/relations/'.format(cfg.root_path)
        rel_filenames = os.listdir(relations_dir)    
        rel_filename = '{}_{}_relations.json'.format(entity_type, kb)

        if rel_filename in rel_filenames:

            with open(relations_dir + rel_filename, 'r') as rel_file:
                extracted_relations = json.loads(rel_file.read())
                rel_file.close()
  
    candidates_dir = check_if_candidates_dir(run_id)

    kb_edges = []
    
    if kb != 'ncbi_gene':
        edges_filepath = kb_dicts_dir + 'node_to_node.json'
        
        with open(edges_filepath, 'r') as dict_file4:
            kb_edges = json.loads(dict_file4.read())
            dict_file4.close() 

    #-------------------------------------------------------------------------
    #                   Build candidates lists for the entities
    #-------------------------------------------------------------------------
    
    # Min lexical similarity between entity text and candidate text: 
    # exclude candidates with a lexical similarity below min_match_score
    min_match_score = 0.0 
    
    # Prepare dataset for candidate generation
    changed_cache_final, \
            kb_cache_up = build_entity_candidate_dict(
                            ner_dir, candidates_dir, 
                            kb, id_to_info, name_to_id, 
                            synonym_to_id, 
                            kb_edges, link_mode, extracted_relations,
                            kb_cache, entity_type, abbreviations, 
                            min_match_score, nil_model_name=nil_mode,
                            nilinker=nilinker)
    
    del nilinker
    del name_to_id
    del synonym_to_id

    if changed_cache_final:
        cache_out = json.dumps(kb_cache_up)
    
        with open(kb_cache_filename, 'wb') as cache_out_file:
            cache_out_file.write(cache_out)
            cache_out_file.close()

        del cache_out
    
    del kb_cache_up
    del kb_cache
    del extracted_relations
    del kb_edges
    #-------------------------------------------------------------------------
    #                  Generate Information content file
    #-------------------------------------------------------------------------
        
    # INTRINSIC INFORMATION CONTENT:
    # Create information content file including every KB concept appearing 
    # in candidates files 
    if kb != 'ncbi_gene':
        generate_ic_file(run_id, candidates_dir, id_to_info)

    # Free up memory usage
    del id_to_info
    garbage_collect()