#!/usr/bin/env python

import random
from rapidfuzz import process, fuzz
from bent.src.REEL.utils import candidate_string


def map_to_kb(
        entity_text, names, synonyms, name_to_id, synonym_to_id, kb, kb_cache, 
        doc_abbreviations):
    """
    Retrieve best knowledge base matches for entity text according to 
    lexical similarity (edit distance).

    :param entity_text: the surface form of given entity 
    :type entity_text: str
    :param names: the strings of all the concepts included in the given 
        knowledge base
    :type names: set
    :synonyms: the strings of all the synonyms of the concepts included in the 
        given knowledge base
    :type synonyms: set
    :param name_to_id: mappings between each KB concept name and 
        respective KB id
    :type name_to_id: dict
    :param synonym_to_id: mappings between each synonym for a 
        given KB concept and respective KB id
    :type synonym_to_id: dict
    :param kb: target knowledge base
    :type kb: str
    :param kb_cache: candidates cache for the given kb
    :type kb_cache: dict
    
    :return: matches (list) with format 
        [{'kb_id': <kb_id>, 'name': <name>, 'match_score': (...)}],
        changed_cache indicating wether the candidates cache was updated
        in the performed mapping or if it remains inaltered, kb_cache_up 
        corresponding to the updated candidates cache (if there was any change)
        or to the same candidates cache
    :rtype: tuple (list, bool, dict)
    """
    
    changed_cache = False 
    top_concepts = []

    if entity_text in doc_abbreviations:
        entity_text = doc_abbreviations[entity_text]

    if entity_text in kb_cache: 
        # There is already a candidate list stored in cache file
        top_concepts = kb_cache[entity_text]

    else:
    
        if entity_text in names: 
            # There is an exact match for this entity
            top_concepts = [(entity_text, 100, 1)]
            kb_cache[entity_text] = top_concepts
            changed_cache = True

        elif entity_text in synonyms: 
            # There is an exact match for this entity
            top_concepts = [(entity_text, 100, 1, 'syn')]
            kb_cache[entity_text] = top_concepts
            changed_cache = True
            
        else:
            # Get first ten KB candidates according to lexical similarity 
            # with entity_text
            top_concepts = None

            if kb == 'ncbi_gene':
                top_concept = process.extractOne(
                    entity_text, names ,scorer=fuzz.token_sort_ratio)
                
                top_concepts = [top_concept]
                
            else:
                top_concepts = process.extract(
                    entity_text, names, limit=10,
                    scorer=fuzz.token_sort_ratio)
                
            if top_concepts[0][1] == 100: 
                # There is an exact match for this entity
                top_concepts = [top_concepts[0]]

            elif top_concepts[0][1] < 100: 
                # Check for synonyms to this entity
                top_synonyms = None

                if kb == 'ncbi_gene':
                    top_synonym = process.extractOne(
                        entity_text, synonyms,scorer=fuzz.token_sort_ratio)

                    top_synonyms = [top_synonym]

                else:
                    top_synonyms = process.extract(
                        entity_text, synonyms, limit=10, 
                        scorer=fuzz.token_sort_ratio)

                for synonym in top_synonyms:

                    if synonym[1] == 100:
                        synoynm_up = (
                            synonym[0], synonym[1], synonym[2], 'syn')
                        top_concepts = [synoynm_up]
                    
                    else:

                        if synonym[1] >= top_concepts[-1][1]:
                            synoynm_up = (
                                synonym[0], synonym[1], synonym[2], 'syn')
                            top_concepts.append(synoynm_up)
            
            kb_cache[entity_text] = top_concepts
            changed_cache = True
       
    # Build the candidates list with match id, name and matching score 
    # with entity_text
    matches = []

    for concept in top_concepts:
        term_name = concept[0]
        term_id = ''

        if len(concept) == 4 and concept[3] == 'syn':
            term_id = synonym_to_id[term_name]

        elif len(concept) == 3:
            term_id = name_to_id[term_name]
        
        else:
            term_id = "NIL"

        match = {"kb_id": term_id,
                 "name": term_name,
                 "match_score": concept[1]/100}
    
        matches.append(match)
    
    return matches, changed_cache, kb_cache


def generate_candidates_list(
        entity_text, kb, id_to_info, names, synonyms, name_to_id, synonym_to_id, 
        kb_cache, min_match_score, doc_abbreviations, kb_id_2_id, 
        nil_candidates=None):
    """
    Build a structured candidates list for given entity text.

    :param entity_text: string of the considered entity
    :type entity_text: str
    :param kb: target knowledge base
    :type kb: str
    :param id_to_info: 
    :type id_to_info: dict
    :param names: the strings of all the concepts included in the given 
        knowledge base
    :type names: set
    :synonyms: the strings of all the synonyms of the concepts included in the 
        given knowledge base
    :type synonyms: set
    :param name_to_id: mappings between each ontology concept name and 
        the respective id
    :type name_to_id: dict
    :param synonym_to_id: mappings between each synonym for a given ontology 
        concept and the respective id
    :type synonym_to_id: dict
    :param kb_cache: candidates cache for the given kb
    :type kb_cache: dict
    :param min_match_score: minimum edit distance between the mention text 
        and candidate string, candidates below this threshold are excluded 
        from candidates list
    :type min_match_score: float
    :param doc_abbreviations: abbreviations identified in the given document
    :type doc_abbreviations: dict
    :param nil_candidates: in cases where the candidates outputed from the 
        'NILINKER' model need to be structured
    :type nil_candidates: list
    :return: candidates_list including all the structured candidates for given
        entity, changed_cache indicating weter the candidates cache was updated
        in the performed mapping or if it remains inaltered, kb_cache_up 
        corresponding to the updated candidates cache (if there was any change)
        or to the same candidates cache
    :rtype: tuple (list, bool, dict)
    """
    
    candidates_list  = []
    less_than_min_score = 0
    
    # Retrieve best KB candidates names and respective ids
    candidate_names = []
    changed_cache = False
    kb_cache_up = {}

    if nil_candidates == None:
        candidate_names, changed_cache, kb_cache_up = map_to_kb(
            entity_text, names, synonyms, name_to_id, synonym_to_id, 
            kb, kb_cache, doc_abbreviations)
     
    else:
        candidate_names = nil_candidates

    # Get properties for each retrieved candidate 
    for candidate in candidate_names: 
        
        if candidate["match_score"] > min_match_score \
                and candidate["kb_id"] != "NIL":
            
            if kb != 'ncbi_gene':

                try:
                    outcount = id_to_info[candidate["kb_id"]][0]
                    incount = id_to_info[candidate["kb_id"]][1]

                except KeyError:
                    incount = 0
                    outcount = 0
                    
            else:
                outcount = 0
                incount = 0
            
            candidate_id = 0

            if candidate["kb_id"] in kb_id_2_id.keys():
                candidate_id = kb_id_2_id[candidate["kb_id"]]
            
            else:
                # generate random id for current candidate
                candidate_id = random.randint(0, 1000000)
                kb_id_2_id[candidate["kb_id"]] = candidate_id
                
            # The first candidate in candidate_names 
            # should be the correct disambiguation for entity
            candidates_list.append(
                {"url": candidate["kb_id"], "name": candidate["name"],
                "outcount": outcount, "incount": incount, "id": candidate_id, 
                "links": [], "score": candidate["match_score"]})
            
        else:
            less_than_min_score += 1
   
    return candidates_list, changed_cache, kb_cache_up, kb_id_2_id


def check_if_related(c1_url, link_mode, extracted_relations, kb_edges, c2_url):
    """
    Check if two given knowledge base concepts/candidates are linked according 
    to the criterium defined by link_mode.

    :param c1: KB concept/candidate 1
    :type c1: str
    :param c2: KB concept/candidate 2
    :type c2: str
    :param link_mode: how the edges are added to the disambiguation graph ('kb',
    'corpus', 'kb_corpus')
    :type link_mode: str
    :param extracted_relations: relations extracted from target corpus
    :type extracted_relations: list
    :param kb_edges: relations described in the knowledge base
    :type kb_edges: list
    
    :return: related, is True if the two candidates are related, False 
             otherwise
    :rtype: bool

    :Example:
    >>> c1 = "ID:01"
    >>> c2 = "ID:02"
    >>> link_mode = "corpus"
    >>> extracted_relations = {"ID:01": ["ID:02"], "ID:03": ["ID:02"]} 
    >>> kb_edges = ["ID:04_ID:O5", "ID:06_ID:07"]
    >>> check_if_related(c1, c2, link_mode, extracted_relations, kb_edges)
    True
    """
   
    related = False

    if link_mode == "corpus":
        # Check if there is an extracted relation between the two candidates
        if c1_url in extracted_relations:
            relations_with_c1 = extracted_relations[c1_url]
                            
            if c2_url in relations_with_c1: 
                # Found an extracted relation
                related = True

    else:
        
        if c1_url == c2_url:
            # There is a KB link between the two candidates
            related = True
                        
        else:
            
            if c1_url in kb_edges and c2_url in kb_edges[c1_url]:
                related = True

            else:

                if c2_url in kb_edges and c1_url in kb_edges[c2_url]:
                    related = True
                    
                else:
                    # There is no KB link between the two candidates
                    # Search in the extracted relations dataset
                                                            
                    if link_mode == "kb_corpus": 
                        # Maybe there is an extracted relation 
                        # between the two candidates
                                        
                        if c1_url in extracted_relations:
                            relations_with_c1 = extracted_relations[c1_url]
                                    
                            if c2_url in relations_with_c1: 
                                # Found an extracted relation
                                related = True
    
    return related


def write_candidates_file(
        kb, doc_entities_candidates, candidates_dir, entity_type, kb_edges, 
        link_mode, extracted_relations, doc_id):
    """Generate the candidates file associated with given document according to 
    the given entities_candidates dictionary that was previously built.

    :param kb: target knowledge base
    :type kb: str
    :param entities_candidates: includes entities of the given document and 
        respective candidates to output
    :type entities_candidates: dict
    :param candidates_dir: path to the directory where the candidates file 
        will be located
    :type candidates_dir: str
     :param entity_type: the type of the entities that will be linked
    :type entity_type: str
    :param kb_edges: includes the edges between knowledge base concepts in the
        format: (concept_1_id, concept_2_id)
    :type kb_edges: list
    :param link_mode: specifies the way the edges are built in the 
        disambiguation graphs that are the input of the PPR algorithm 
        ('corpus' - extracted relations from an external corpus, 
        'kb' - relations described in the knowledge base, 
        'kb_corpus' - extracted relations from an external corpus and relations
        described in the knowledge base, 
    :type link_mode: str
    :param extracted_relations: includes extracted relations from external 
        dictionary or is empty if link_mode=kb
    :type extracted_relations: list
    """
    
    candidates_filename = candidates_dir + doc_id
    candidates_file = open(candidates_filename, 'w')

    for annotation1 in doc_entities_candidates:
        entity_str = annotation1[0]
        candidates_file.write(entity_str)
    
        for c1 in annotation1[1]:
            c1["links"] = ''

            if kb != 'ncbi_gene':
                # Find links between the candidates in the current document
            
                # Get all the candidates for the remaining entities in the 
                # same document
                other_candidates = [(c2['url'], c2['id']) for annotation2 in 
                    doc_entities_candidates if annotation1[0] != annotation2[0] 
                    for c2 in annotation2[1]]

                # Check if there is a relation between current candidate and each
                # of the candidates for the remaining entities
                id_links = [str(c2[1]) for c2 in other_candidates 
                                if check_if_related( 
                                    c1['url'], link_mode, 
                                    extracted_relations, 
                                    kb_edges, c2[0])]

                # The ids of the candidates are needed instead of the KB ids
                c1["links"] = ";".join(set(id_links))

            candidates_file.write(
                candidate_string.format(c1["id"], c1["incount"], c1["outcount"], 
                c1["links"], c1["url"], c1["name"], c1["name"].lower(), 
                c1["name"].lower(), entity_type))
                
    candidates_file.close()
