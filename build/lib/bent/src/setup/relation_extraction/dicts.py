#!/usr/bin/env python

# Build dictionaries of extracted relations to further inclusion in the NEL module
import bent.src.cfg as cfg
import json
import pandas as pd

datasets_dir = cfg.root_path + 'data/datasets/'
relations_dir = cfg.root_path + 'data/relations/'


def update_dict(id1, id2, relations):

    if id1 not in relations:
        relations[id1] = [id2]
                    
    else:

        if id2 not in relations[id1]:
            relations[id1].append(id2)

    return relations


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


def import_chr_relations():
    """Get the relations (ChEBI-ChEBI) described in the CHR corpus.
    
    :return: relations, with format 
        {"chebi_id1": [chebi_id2, chebi_id3]}
    :rtype: dict
    """

    relations = dict()
    corpus_dir = datasets_dir + 'CHR_corpus/'
    filenames = ['train.pubtator', 'dev.pubtator', 'test.pubtator']

    for filename in filenames:

        with open(corpus_dir + filename, 'r') as corpus_file:
            data = corpus_file.readlines()
            corpus_file.close()
           
            for line in data:
                line_data = line.split("\t")
                
                if len(line_data) == 4:

                    annotation1 = line_data[2]
                    annotation2 = line_data[3]

                    entity1 = check_if_annotation_is_valid(annotation1)
                    entity2 = check_if_annotation_is_valid(annotation2)
                    
                    if entity1 != '' and entity2 != '':
                        relations = update_dict(entity1, entity2, relations)
                        relations = update_dict(entity2, entity1, relations)
        
    return relations


def import_hpo_annotations(entity_type):
    """Builds dict with disease-disease relations from the HPO file 
    'phenotype_to_genes.txt'.
    
    :return: relations, with format {"hp_id1": [hp_id2, hp_id3, ...]} if
        entity_type = 'phenotype' or with format 
        {gene_id: [gene_id2, gene_id3, ...]} if entity_type = 'gene'
    :rtype: dict"""
    
    annotations_path = datasets_dir + 'phenotype_to_genes.txt' 

    with open(annotations_path, 'r') as annotations_file:
            data = annotations_file.readlines()
            annotations_file.close()

    relations_temp  = dict()
    line_count = 0

    for line in data:

        if line_count > 1:
            hp_id = line.split("\t")[0].replace(":","_")
            gene_id = line.split("\t")[2]

            if entity_type == 'phenotype':
                relations_temp = update_dict(gene_id, hp_id, relations_temp)

            elif entity_type == 'gene':
                relations_temp = update_dict(hp_id, gene_id, relations_temp)

        line_count += 1
    
    relations = dict()
    
    for key in relations_temp:
        entities = relations_temp[key]
        
        for entity1 in entities:
            
            for entity2 in entities:            

                if entity1 != entity2:
                    relations = update_dict(entity1, entity2, relations)
                    relations = update_dict(entity2, entity1, relations)

    return relations


def parse_bc5cd5_relations(entity_type, subset):
    """
    Import chemical-disease interactions from BC5CDR corpus in PubTator format 
    into dict.

    :param dataset: the target dataset
    :type dataset: str
    :param subset:  either "train", "dev", "test" or "all"
    :type subset: str
    
    :return: relations, with format 
        {"disease_id1": [disease_id2, disease_id3]}
    :rtype: dict
    """

    corpus_dir = datasets_dir + 'CDR_Data/CDR.Corpus.v010516/'
    filenames = []
    relations = {}
    relations_temp  = {}
    
    if subset == "train":
        filenames.append("CDR_TrainingSet.PubTator.txt")
    
    elif subset == "dev":
        filenames.append("CDR_DevelopmentSet.PubTator.txt")
    
    elif subset == "test":
        filenames.append("CDR_TestSet.PubTator.txt")
    
    elif subset == "all":
        filenames.append("CDR_TrainingSet.PubTator.txt")
        filenames.append("CDR_DevelopmentSet.PubTator.txt")
        filenames.append("CDR_TestSet.PubTator.txt")
  
    for filename in filenames:
        
        with open(corpus_dir + filename, 'r') as corpus_file:
            data = corpus_file.readlines()
            corpus_file.close()
           
            for line in data:
                line_data = line.split("\t")
                
                if len(line_data) == 4 and line_data[1] == "CID":
                    # Chemical-disease Relation 
                    chemical_id = 'MESH_' + line_data[2]
                    disease_id = 'MESH_' + line_data[3].strip("\n")

                    if entity_type == "disease":
                        # Get the disease-disease relations
                        relations_temp = update_dict(
                            chemical_id, disease_id, relations_temp)
                    
                    elif entity_type == "chemical":
                        # Get the chemical-chemical relations
                        
                        relations_temp = update_dict(
                            disease_id, chemical_id, relations_temp)

    # Two disease terms are related if associated with the same chemical
    # Two chemical terms are related if associated with the same disease
    for key in relations_temp:
        entities = relations_temp[key]
        
        for entity1 in entities:
            
            for entity2 in entities:            

                if entity1 != entity2:
                    relations = update_dict(entity1, entity2, relations)
                    relations = update_dict(entity2, entity1, relations)

    return relations
 

def buid_dict(entity_type, kb):

    filenames = []
    
    if entity_type == 'chemical':

        if kb == 'chebi':
            filenames = ['CHR']
        
        elif kb == 'ctd_chem':
            filenames = ['BC5CDR_train', 'BC5CDR_dev']

    elif entity_type == 'disease':
        
        if kb == 'medic':
            filenames = ['BC5CDR_train', 'BC5CDR_dev']

    elif entity_type == 'bioprocess':
        pass

    elif entity_type == 'gene':
        
        if kb == 'ncbi_gene':
            filenames = ['phenotype_to_genes.txt']

    elif entity_type == 'phenotype':

        if kb == 'hp':
            filenames = ['phenotype_to_genes.txt']

    # Import the relations associated with given entity_type
    relations = dict()

    for filename in filenames:

        if filename == 'phenotype_to_genes.txt':
            imported_relations = import_hpo_annotations(entity_type)

        elif filename[:6] == 'BC5CDR':
            subset = filename.split('_')[1]
            imported_relations = parse_bc5cd5_relations(entity_type, subset)

        elif filename == 'CHR':
            imported_relations = import_chr_relations()

        relations = {**relations, **imported_relations}
    
    # Output json file with the relations
    outfilename = '{}_{}_relations.json'.format(entity_type, kb)
    output = json.dumps(relations, indent=4)

    with open(relations_dir + outfilename, 'w') as outfile:
        outfile.write(output)
        outfile.close()
    

def build_relations_dicts():
      
    pairs = [('disease', 'medic'), ('chemical', 'chebi'), 
        ('bioprocess', 'go_bp'), ('gene', 'ncbi_gene'), ('chemical', 'ctd_chem')]
   
    for pair in pairs:
        buid_dict(pair[0], pair[1])