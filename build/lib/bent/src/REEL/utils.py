
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


def check_if_candidates_dir(run_id):

    candidates_dir = f".tmp/{run_id}/REEL/candidates/"

    # Create directories for candidates files
    os.makedirs(candidates_dir, exist_ok=True)

    cand_files = os.listdir(candidates_dir)
    
    if len(cand_files)!=0:
        
        for file in cand_files:
            os.remove(candidates_dir + file)

    return candidates_dir


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