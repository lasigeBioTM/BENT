
#!/usr/bin/env python

import logging
import os
import sys
from rapidfuzz import process, fuzz
sys.path.append("./")

# String formats for entities and candidates
entity_string = "ENTITY\ttext:{0}\tnormalName:{1}\tpredictedType:{2}\tq:true"
entity_string += "\tqid:Q{3}\tdocId:{4}\torigText:{0}\turl:{5}\n"
candidate_string = "CANDIDATE\tid:{0}\tinCount:{1}\toutCount:{2}\tlinks:{3}\t"
candidate_string += "url:{4}\tname:{5}\tnormalName:{6}\tnormalWikiTitle:{7}\t\
    predictedType:{8}\n"


def stringMatcher(entity_text, name_to_id, top_k):
    """
    Finds top KB candidate for given entity according to lexical similarity 
    (edit distance).

    :param entity_text: the surface form of given entity 
    :type entity_text: str
    :param name_to_id: mappings between each kb concept name and 
        the respective id
    :type name_to_id: dict
    
    :return: (top_candidate_name, top_candidate_id)
    :rtype: tuple
    
    :Example:
    >>> entity_text = "pneumonia",
    >>> name_to_id = {"pneumonia": "ID:01", "cancer": "ID:02"}
    >>> stringMatcher(entity_text, name_to_id)
    pneumonia, ID:01
    
    """

    top_candidates = process.extract(
        entity_text, name_to_id.keys(), scorer=fuzz.token_sort_ratio, limit=top_k)

    top_candidates_out = list()

    for candidate in top_candidates:
        top_candidate_name = candidate[0]
        top_candidate_id = name_to_id[top_candidate_name]
        score = candidate[1]
        candidate_out = (top_candidate_id, top_candidate_name, score)
        top_candidates_out.append(candidate_out)
    
    return top_candidates_out


def check_if_candidates_dir(run_id):#, link_mode, nil_mode):
    """asffssf"""

    candidates_dir = '.tmp/{}/REEL/candidates/'.format(run_id) 

    # Create directories for candidates files
    if not os.path.exists(candidates_dir):
        os.mkdir(candidates_dir)

    cand_files = os.listdir(candidates_dir)
    if len(cand_files)!=0:
        
        for file in cand_files:
            os.remove(candidates_dir + file)

    return candidates_dir


def get_stats(doc_count, total_entities_count, unique_entities_count, 
              solution_is_first_count, run_id, link_mode, nil_mode):
    """
    Calculates statistics for given model, print the statistics and generate a 
    file.

    :param dataset: the target dataset
    :type dataset: str
    :param doc_count: number of documents
    :type doc_count: int
    :param total_entities_count: number of entities in given dataset
    :type total_entities_count: int
    :param unique_entities_count: number of unique entities in each document of
        the dataset
    :type unique_entities_count: int
    :param solution_is_first_count: number of correct predictions
    :type solution_is_first_count: int
    :param nil_count: number of NIL entities
    :type nil_count: int
    """

    logging.info("Calculating statistics")    
    # For the calculation of metrics, only unique entities in a document are
    # considered. For example, if the entity "pneumonia" appears twice in a 
    # given document, only one mention is included in the calculation

    tp = solution_is_first_count
    fp = unique_entities_count-solution_is_first_count#-nil_unique_count
    accuracy = tp/unique_entities_count
   
    stats = str()
    stats += "------\nNumber of documents: " + str(doc_count)  
    stats += "\nTotal unique entities: " + str(unique_entities_count)
    stats += "\nCorrect disambiguations (TP): " + str(solution_is_first_count)
    stats += "\nWrong Disambiguations (FP): " + str(fp)
    stats += "\nAccuracy: " + str(accuracy)
    
    print(stats)


def check_if_annotation_is_valid(annotation):

    output_kb_id = ''

    if '|' in annotation:
        # There are entities associated with two kb_ids, e.g.:
        # HMDB:HMDB01429|CHEBI:18367
        output_kb_id = annotation.split('|')[1].replace(':', '_')

        if output_kb_id[:4] == 'HMDB':
            output_kb_id = annotation.split('|')[0].replace(':', '_')
         
    else:
        
        if annotation[:5] == 'CHEBI':
            output_kb_id = annotation.replace(':', '_')
        
    output_kb_id = output_kb_id.strip('\n')

    # Check if output entity is valid
    assert output_kb_id[:5] == 'CHEBI' or output_kb_id == ''

    return output_kb_id