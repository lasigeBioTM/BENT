#!/usr/bin/env python
import bent.src.cfg as cfg
import orjson as json 
import os
import psutil
import shutil
import gc
from bent.src.classes import Document, Sentence, Entity
from copy import deepcopy

#------------------------------------------------------------------------------
#                       INPUT ARGUMENTS VERIFICATION
#------------------------------------------------------------------------------

def check_input_types(types):
    """Check if the inputted entity types are valid, as well the selected 
    target knowledge bases.

    :param types: a dictionary with the format {'entity_type: 'target_kb'}
    :type types: dict
    :raises ValueError: if types is an empty dictionary 
    """
    
    if types == {}:
        raise ValueError('No specified entity types!')
    
    else:
        available_kbs = {'disease': ['medic', 'do', ''], 
                        'chemical': ['ctd_chem', 'chebi', ''],
                        'gene': ['ncbi_gene', 'ctd_gene'],
                        'organism': ['ncbi_taxon', ''],
                        'bioprocess': ['go_bp', ''],
                        'anatomical': ['ctd_anat', 'uberon', ''] ,
                        'cell_component': ['go_cc', ''],
                        'cell_line': ['cellosaurus', ''],
                        'cell_type': ['cl', ''],
                        'variant': ['']
                        }

        for ent_type in types:
            
            if ent_type != '':
                assert ent_type in available_kbs, \
                    '{} is an invalid entity type! Options:\
                    "disease", "chemical", "gene", "organism", "bioprocess", \
                    "bioprocess", "anatomical", "cell_component", "cell_line",\
                    "cell_type", "variant"'.format(ent_type)
                
                target_kb = types[ent_type]
                
                assert target_kb in available_kbs[ent_type], \
                    '{} is an invalid KB for entity type "{}"! Options:\
                    {}'.format(target_kb, ent_type, str(available_kbs[ent_type]))          


def check_input_args(recognize, link, types, input_format, input_text, 
        in_dir, ner_dir, out_dir, ner_model, nel_model):
    """Verify if the input arguments are valid"""

    available_formats = ['brat', 'bioc_xml', 'bioc_json', 'pubtator'] 

    # Verify selected task(s)
    assert recognize == True or link == True, \
        'It is available Named Entity Recognition (NER) and/or Named Entity \
        ensure that either recognize == True and/or link == True'

    # Verify the inputed entity types and respective target KBs
    check_input_types(types)

    # Verify input format and dir
    if recognize:

        if input_text == None and in_dir == None:
            raise ValueError('It is necessary to input either a text \
                ("input_text") OR a directory containing file(s) with text \
                to annotate ("text_dir").') 
        
        if input_format == 'bioc_json' or input_format == 'bioc_xml' \
                or input_format == 'pubtator':

                assert in_dir != None or ner_dir != None, \
                    'For input formats "bioc_json"\
                    , "bioc_xml"and "pubtator" it is necessary to specify\
                    the input directory "in_dir"'

    if link:

        if not recognize:

            assert ner_dir != None, 'It is necessary to specfiy the directory \
                containing the ouput from the NER stage ("ner_dir").' 

    #Check directories paths
    if in_dir != None:
        assert in_dir[-1:] == '/', 'Invalid "in_dir". Last character in \
            directory name must be "/"'

    if ner_dir != None:
        assert ner_dir[-1:] == '/', 'Invalid "ner_dir". Last character in \
            directory name must be "/"'

    if out_dir != None:
        assert out_dir[-1:] == '/', 'Invalid "out_dir". Last character in \
            directory name must be "/"'
        

#------------------------------------------------------------------------------
#                       INPUT FILE FORMAT CONVERSION
#------------------------------------------------------------------------------

def parse_bioc_json_file(filename, include_text=True):
    

    with open(filename, 'r') as infile:
        parsed_data = json.loads(infile.read())
        infile.close()

    parsed_data_up = {}

    for doc in parsed_data['documents']:
        title = ''
        abstract = ''
        annotations = []
        parsed_data_up[doc['id']] = ['', []]

        for passage in doc['passages']:
            
            if passage['infons']['type'] == 'title':
                title = passage['text']

            if passage['infons']['type'] == 'abstract':
                abstract = passage['text']

                for annot in passage['annotations']:
                    ent_type = annot['infons']['type']
                    #kb_id = annot['infons']['identifier']
                    text = annot['text']

                    begin = annot['locations'][0]['offset']
                    end = str(int(begin) + int(annot['locations'][0]['length']))

                    annotation = (ent_type, begin, end, text)
                    annotations.append(annotation)
        
        text = title + '\n' + abstract
        
        parsed_data_up[doc['id']][0] = ''

        if include_text:
            parsed_data_up[doc['id']][0] = text
        
        parsed_data_up[doc['id']][1] = annotations

    return parsed_data_up


def output_parsed_docs(parsed_data, out_dir, recognize=False):

    # Output parsed documents to out_dir in the BRAT format
    if not os.path.exists(out_dir + 'txt/'):
        os.mkdir(out_dir + 'txt/')
    
    if not os.path.exists(out_dir + 'ann/'):
        os.mkdir(out_dir + 'ann/')

    for doc_id in parsed_data:
        doc_text = parsed_data[doc_id][0]
        
        with open(out_dir + 'txt/' + doc_id + '.txt', 'w') as txt_file:
            txt_file.write(doc_text)
            txt_file.close()
       
        if not recognize:
            # In this case only the NEL step will be performed
            # Make annotations file
        
            annotations = parsed_data[doc_id][1]
            annot_str = ''

            for i, annot in enumerate(annotations):
                annot_str += 'T{}\t{} {} {}\t{}\n'.format(
                    str(i+1), annot[0], annot[1], annot[2], annot[3]) 
        
            with open(out_dir + 'ann/' + doc_id + '.ann', 'w') as ann_file:
                ann_file.write(annot_str)
                ann_file.close()
        

def convert_input_files(format, input_text=None, in_dir=None, recognize=False):
    """Convert input file(s) into brat/standoof format"""
    
    if input_text != None:

        if type(input_text) == str:
            input_files = [input_text]
            
        elif type(input_text) == list:
            input_files = input_text

        # Create a txt file for later use in the NEL module.
        for i, text in enumerate(input_files):
            doc_id = str(i)
            
            with open(out_dir + doc_id + '.txt', 'w') as txt_file:
                txt_file.write(text)
                txt_file.close()
    
    else:

        assert format == 'bioc_xml' or format == 'bioc_json' \
            or format == 'pubtator',  'Invalid format. Options: "brat", \
            "bioc_xml", "bioc_json", "pubtator"'
        
        
        filenames = [in_dir + filename for filename in os.listdir(in_dir)]
        out_dir = in_dir + 'brat/'
            
        for filename in filenames:
            output = False
            
            if format == 'bioc_xml' and filename[-3:] == 'xml':
                parsed_data = parse_bioc_xml_file(filename)
                output = True
            
            elif format == 'bioc_json' and filename[-4:] == 'json':
                parsed_data = parse_bioc_json_file(filename)
                output = True
           
            elif format == 'pubtator' and filename[-3:] == 'txt':
                parsed_data = parse_pubtator_file(filename)
                output = True

            if output:

                if not os.path.exists(out_dir):
                    os.mkdir(out_dir)
                
                output_parsed_docs(parsed_data, out_dir, recognize=recognize)
        

#------------------------------------------------------------------------------
#                       TEXT PARSING AND OBJECTIFICATION 
#------------------------------------------------------------------------------

def sentence_splitter(doc_text, lang_model):
    """Split given text into sentences using SpaCy and the ScispaCy model 
    'en_core_sci_lg' (https://allenai.github.io/scispacy/).

    :param doc_text: the input text to be splitted into sentences
    :type doc_text: str
    :param lang_model: Spacy sentence splitter model
    :type lang_model:
    :return: doc_sentences including input text splitted in sentences 
    :rtype: list
    """
  
    processed_doc = lang_model(doc_text)
    doc_sentences = [sent.text for sent in processed_doc.sents]
    
    return doc_sentences


def objectify_ner_input(doc_id, doc_text, doc_sentences):
    """Convert a given input text into a Document object.

    :param doc_id: the idenfitifer of the input text
    :type doc_id: str
    :param doc_text: the input text
    :type doc_text: str
    :param doc_sentences: the sentences of the input text
    :type doc_sentences: list
    :return: doc_obj including all the information about the input text, such 
        as its identifier and its sentences 
    :rtype: Document objcet
    """
    
    # Hierarchy: Collection -> Document -> Sentence -> Entity
    doc_obj = Document(doc_text)
    doc_obj.set_id(doc_id)
    current_pos = 0
    last_sent_index = len(doc_sentences) -1
    doc_text_len = len(doc_text) 
   
    for i, sent_text in enumerate(doc_sentences):
        #---------------------------------------------------------------------
        # Solve mismatches produced by the sentence splitter when current
        # sentence and previous sentence are not separated by ' '.
        # This allows the correction of the span of the recognized entities
        
        if sent_text.isalnum():
                    
            try:
                if i == last_sent_index:
                    original_char = (doc_text[current_pos-1])
                
                elif i < last_sent_index:
                    original_char = (doc_text[current_pos])
                
                if original_char == ' ':
                    i = 0
                    proceed = True
                    
                    while proceed:
                        current_pos += 1
                        
                        if current_pos < (doc_text_len):
                            original_char = (doc_text[current_pos])
                            
                            if original_char != ' ':
                                proceed = False
                        
                        else:
                            proceed = False

                        i += 1
                    
                else:
                    sent_first_char = sent_text[0]

                    if original_char != sent_first_char:
                        i = 0
                        
                        while original_char != sent_first_char:
                            current_pos -= 1
                            original_char = (doc_text[current_pos])
                            i += 1      

            except IndexError:
                continue  
        #---------------------------------------------------------------------
        sent_start = current_pos 
        sent_end = current_pos + len(sent_text)
        sent_obj = Sentence(sent_start, sent_end, sent_text)
        sent_obj.set_num(i)
        
        doc_obj.add_sentence(sent_obj) 

        # Usually sentences are separated by ' ', so it is added 1 to the 
        # current position but in some cases this is not true
        current_pos += len(sent_text) + 1
    
    return doc_obj


def objectify_entities(entities, sent_pos, includes_links=False):
    """Convert inputted recognized entities into Entity objects.

    :param entities: entities to be objectified
    :type entities: list
    :param sent_pos: the position of the sentence where the input entities 
        were recognized relative to the source document 
    :type sent_pos: int
    :param includes_links: specifies if there are knowledge based identifiers 
        associated with the input entities, defaults to False
    :type includes_links: bool, optional
    :return: entities_obj including the Entity objects relative to the input 
        entities 
    :rtype: list
    """

    entities_obj = []

    for entity in entities:
        kb_id = None

        if len(entity) == 2:
            entity_obj = Entity(None, None, entity[0], entity[1], None, None, 
                None)

        elif len(entity) > 2:

            if includes_links:
                kb_id = entity[4]
                entity_obj = Entity(
                    entity[0], entity[1], entity[2], entity[3], kb_id, 
                    entity[5], sent_pos)
            
            else:
                kb_id = None
                entity_obj = Entity(
                    entity[0], entity[1], entity[2], entity[3], kb_id, 
                    entity[4], sent_pos)
            
        entities_obj.append(entity_obj)

    return entities_obj


#------------------------------------------------------------------------------
#                        FORMAT OUTPUT
#------------------------------------------------------------------------------

def prepare_output_from_objects(doc, only_ner=True):
    """Output given dataset in BRAT format to the given directory"""

    doc_annots = ''
    normalizations = ''
    
    for i, entity in enumerate(doc.entities):
        doc_annots += 'T{}\t{} {} {}\t{}\n'.format(
            str(i+1), entity.type, entity.start, entity.end, entity.text) 

        if not only_ner:
            normalizations += 'N{}\tReference T{} {}\t{}\n'.format(
                str(i+1), str(i+1), entity.kb_id, entity.text)

    if not only_ner:
        doc_annots += normalizations
    
    return doc_annots   


def merge_dicts(dict1, dict2):
    
    dict3 = {}
    overlapping_keys = dict1.keys() & dict2.keys()

    for key in overlapping_keys:
        dict3[key] = merge_dicts(dict1[key], dict2[key])

    for key in dict1.keys() - overlapping_keys:
        dict3[key] = deepcopy(dict1[key])

    for key in dict2.keys() - overlapping_keys:
        dict3[key] = deepcopy(dict2[key])

    return dict3


def import_reel_results(doc_id, nel_run_ids):
    """Parse the results outputted by REEL-NILINKER for given document from 
    file into a dictionary.

    :param doc_id: the identifier of the document where the entities were 
        recognized 
    :type doc_id: str
    :param nel_run_ids: identifiers that allow the parsing of the output of the 
        Named Entity Linking step from files
    :type nel_run_ids: list
    :return: linked_entities with format: {'entity_text': 'kb_id'}
    :rtype: dict
    """
    
    linked_entities = {}

    for run_id in nel_run_ids:
        results_dir = '{}{}/REEL/results/'.format(cfg.tmp_dir, run_id)
        results_files = os.listdir(results_dir)
        linked_entities_type = {}       
        ent_type = run_id.split('_')[1] 
        target_filename = doc_id + '.json'

        if target_filename in results_files:
            filepath = results_dir + target_filename
            
            with open(filepath, 'r') as infile:
                linked_entities_type = json.loads(infile.read())
                infile.close()

        if linked_entities_type != {}:
            # Transform the keys of linked_entities_type
            linked_entities_type_up = {}

            for key in linked_entities_type.keys():
                key_name = key + '_' + ent_type
                linked_entities_type_up[key_name] = linked_entities_type[key]
    
            linked_entities = merge_dicts(
                linked_entities, linked_entities_type_up)
   
    return linked_entities


def update_dataset_with_nel_output(dataset, nel_run_ids):
    """Update Dataset object containing recognized entities (Named Entity 
    Recognition step) with the output of the Named Entity Linking pipeline, 
    i.e. knowledge base identifiers for each recognized entity.

    :param dataset: includes the output of the Named Entity Recognition 
        pipeline
    :type dataset: Dataset object
    :param nel_run_ids: identifiers that allow the parsing of the output of the 
        Named Entity Linking step from files
    :type nel_run_ids: list
    :return: updated dataset combining Named Entity Recognition + Linking
        outputs
    :rtype: Dataset object
    """
    
    dataset_docs = dataset.documents   

    for doc in dataset_docs:
        linked_entities = import_reel_results(doc.id, nel_run_ids)
        
        for i, sent in enumerate(doc.sentences):
            sent_entities = sent.entities

            for entity in sent_entities:
                key_name = entity.text + '_' + entity.type
                
                if key_name in linked_entities.keys():
                    kb_id = linked_entities[key_name][0]
                    entity.set_kb_id(kb_id)        
                    sent.update_entity(entity)
            
            doc.update_sentence(sent, i)

    dataset.update_doc(doc, doc.id) 

    return dataset 


def update_ner_file_with_nel_output(ner_dir, nel_run_ids, out_dir=None):
    """Update annotations file generated in the Named Entity Recognition step
    with the output of the Named Entity Linking pipeline, i.e. knowledge base 
    identifiers for each recognized entity. The generated annotations files 
    will be located in the directory 'ner_dir'.

    :param ner_dir: path to directory where the recognized entities are
        stored in the annotations files
    :type ner_dir: str
    :param nel_run_ids: identifiers that allow the parsing of the output of the 
        Named Entity Linking step from files
    :type nel_run_ids: list
    :param out_format: the format of the ouput, defaults to 'brat'
    :type out_format: str, optional
    """
        
    ner_filenames = os.listdir(ner_dir)

    for filename in ner_filenames:
        doc_id = filename.strip('.ann')
        linked_entities = import_reel_results(doc_id, nel_run_ids)
        complete_filepath = ner_dir + filename
        
        with open(complete_filepath, 'r') as ner_file:
            ner_output = ner_file.readlines()
            ner_file.close()
   
        # Add the normalization lines to the annotations file
        final_output = ''

        for line in ner_output:
            
            if line != '\n':
                entity_text = line.split('\t')[2].strip('\n')
                term_id = line.split('\t')[0]
                entity_type = line.split('\t')[1].split(' ')[0]
                final_output += line

                if final_output[-1:] != '\n':
                    final_output += '\n'
                
                key_name = entity_text + '_' + entity_type
                
                if key_name in linked_entities.keys() and term_id[0] == 'T':
                    kb_id = linked_entities[key_name][0]
                    final_output += 'N{}\tReference {} {}\t{}\n'.format(
                        term_id.split('T')[1], term_id, kb_id, entity_text)
        
        if final_output[-1:] == '\n':
            final_output = final_output[:-1]

        if out_dir != None:
            out_filepath = out_dir + filename

            if not os.path.exists(out_dir):
                os.mkdir(out_dir)

        with open(out_filepath, 'w' ) as out_file:
            out_file.write(final_output)   
            out_file.close()   

    # Delete temporary files associated with given run_ids
    for run_id in nel_run_ids:
        dir_to_delete = cfg.tmp_dir + run_id
        shutil.rmtree(dir_to_delete, ignore_errors=True)


#------------------------------------------------------------------------------
#                           OTHER
#------------------------------------------------------------------------------

def garbage_collect(threshold=50.0):
    """Call the garbage collection if memory usage is greater than threshold.

    :param threshold: amount of memory usage that triggers the garbage 
        collection, defaults to 50.0
    :type threshold: float, optional
    """

    if psutil.virtual_memory().percent >= threshold:
        gc.collect()