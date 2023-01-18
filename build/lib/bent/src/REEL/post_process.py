#!/usr/bin/env python

import bent.src.cfg as cfg
import orjson as json
import os


def process_results(run_id, entity_type, kb):
    """Process the results after the application of the PPR-IC model and
    output a JSON file in the directory 'tmp/REEL/results/<run_id>/."""

    if kb != 'ncbi_gene':
        results_filepath = '{}{}/REEL/results/candidate_scores'.format(
            cfg.tmp_dir, run_id)

        # Import PPR output
        with open(results_filepath, 'r') as results:
            data = results.readlines()
            results.close
    
        linked_entities = {}
        doc_id = ''
        
        for line in data:
            
            if line != '\n':
                
                if line[0] == '=':
                    doc_id = line.strip('\n').split(' ')[1]
                    
                else:
                    entity = line.split('\t')[1].split('=')[1]           
                    answer = line.split('\t')[3].split('ANS=')[1].strip('\n').\
                        replace('_', ':')
            
                    if doc_id in linked_entities.keys():
                        linked_entities[doc_id][entity] = (answer, entity_type)
                    
                    else:
                        linked_entities[doc_id] = {entity: (answer, entity_type)}
    
    elif kb == 'ncbi_gene':
        results_filepath = cfg.tmp_dir + run_id + '/REEL/candidates/'
        results_files = os.listdir(results_filepath)
        linked_entities = {}
        found_entity = False

        for file in results_files:

            with open(results_filepath + file, 'r') as results:
                data = results.readlines()
                results.close()
                entity = ''

                for line in data:
                    
                    if found_entity:
                        # This is the top candidate
                        answer = line.split('url:')[1].split('\t')[0].\
                            replace('_', ':')
                        
                        if file in linked_entities:
                            linked_entities[file][entity] = (answer, 'gene')
                        
                        else:
                            linked_entities[file] = {entity: (answer, 'gene')}

                        found_entity = False
                        entity = ''
                    
                    else:

                        if line[0] == 'E':
                            entity = line.split('\t')[1].strip('text:')
                            found_entity = True
    
    out_dir = '{}{}/REEL/results/'.format(cfg.tmp_dir, run_id)
    
    for doc in linked_entities.keys():
        doc_results = linked_entities[doc]
        out_json = json.dumps(doc_results)

        with open(out_dir + doc + '.json', 'wb') as out_file:
            out_file.write(out_json)
            out_file.close()