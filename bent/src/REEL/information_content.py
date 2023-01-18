#!/usr/bin/env python

import os
from math import log


def build_term_counts(candidates_dir):
    """Build a dict containing the frequency of each candidate entity that 
    appears in the candidates files generated during the pre-processing stage.
    """

    term_counts = {}

    candidates_files = os.listdir(candidates_dir)
    
    # Get the term frequency in the corpus
    for filename in candidates_files: 

        lines = open(candidates_dir + filename, 'r').readlines()
        
        for line in lines:

            if line[:9] == 'CANDIDATE':
                url = line.split('\t')[5].split('url:')[1]

                if url not in term_counts.keys():
                    term_counts[url] = 1
                
                else:
                    term_counts[url] += 1

    return term_counts


def build_information_content_dict(candidates_dir, id_to_info, mode=None):
    """Generate dictionary with the information content for each candidate 
    term. For more info about the definition of information content see
    https://www.sciencedirect.com/science/article/pii/B9780128096338204019?via%3Dihub""" 

    term_counts = build_term_counts(candidates_dir)
    
    ic = {}
    total_terms = 0

    if mode == 'intrinsic':
        total_terms = len(id_to_info.keys())

    for term_id in term_counts:        
        
        term_probability = float()

        if mode == 'extrinsic':
            # Frequency of the most frequent term in dataset
            max_freq = max(term_counts.values()) 
            term_frequency = term_counts[term_id] 
            term_probability = (term_frequency + 1)/(max_freq + 1)
        
        elif mode == 'intrinsic':
            
            try:
                num_descendants = id_to_info[term_id][2]
                term_probability = (num_descendants + 1) / total_terms
                
            except:
                term_probability = 0.000001

        else:
            raise ValueError('Invalid mode!')
        
        information_content = -log(term_probability) + 1
        ic[term_id] = information_content + 1
    
    return ic


def generate_ic_file(run_id, candidates_dir, id_to_info):
    """Generate file with information content of all entities present in the 
    candidates files."""

    ic = build_information_content_dict(
        candidates_dir, id_to_info, mode='intrinsic') 

    # Build output string
    out_string = str()

    for term in ic.keys():
        out_string += term +'\t' + str(ic[term]) + '\n'

    # Create file ontology_pop with information content for all entities 
    # in candidates file
    out_dir = ".tmp/{}/REEL/".format(run_id)

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    output_file_name = out_dir + "ic" 

    with open(output_file_name, 'w') as ic_file:
        ic_file.write(out_string)
        ic_file.close()