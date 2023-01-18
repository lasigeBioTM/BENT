#!/usr/bin/env python
import os
import random
import string
import spacy
from tqdm import tqdm
import bent.src.utils as utils
from bent.src.ner import ner
from bent.src.nel import nel
from bent.src.classes import Dataset


def recognizer(in_dir, input_text, entity_types, out_dir, ner_model, run_id):
    """Pipeline to perform Named Entity Recognition. For each input 
    document/text it outputs either an annotations file (BRAT format) or a 
    Dataset object including all documents and respective annotations.

    :param in_dir: path to directory containing text files to be annotated, 
        defaults to None
    :type in_dir: _type_, optional
    :param input_text: text string or list of text strings (each element 
        represinting a different document) to be annotated, defaults to None
    :type input_text: str or list, optional
    :param types: the entity types that will be recognized 
        :type types: list
    :param out_dir: path to directory where the output of the pipeline will be
        located, optional. If 'out_dir' == None (deafult) a Dataset object 
        including all documents and respective annotations will be returned  
    :type out_dir: str, defaults to None
    :param ner_model: the Named Entity Recognition model that will be used, 
        defaults to 'pubmedbert'
    :type ner_model: str, optional
    :return: dataset (an object including all the input texts along with the 
        annotations) if 'out_dir' is None; an annotation file for each inputed
        text if 'out_dir' is different that None
    :rtype: Dataset object, text file(s)
    """
    
    # Disable printing of annoying messages
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # Spacy language model to segment the inputed texts into sentences 
    lang_model = spacy.load('en_core_sci_lg')
    stopwords = lang_model.Defaults.stop_words
    
    # Load the NER models that will be used
    recognizer = ner(ner_model, entity_types, stopwords)

    # Wether the input is a directory with text files or not
    filename_mode = False 

    dataset = Dataset()

    if out_dir == None:
        # In this case a dataset object will be outputted and the 
        # temporary annotation files will be stored in 'tmp/NER/' directory
        tmp_out_dir = '.tmp/{}/'.format(run_id)
        os.mkdir(tmp_out_dir)

    if recognizer.model_type == "bert":  
        input_files = None

        if in_dir != None:
            filename_mode = True
            input_files = [
                in_dir + filename for filename in os.listdir(in_dir)]
            
        elif input_text != None:
            
            if type(input_text) == str:
                input_files = [input_text]
            
            elif type(input_text) == list:
                input_files = input_text

        # Recognize entities in each document
        pbar = tqdm(total=len(input_files), colour= 'green', 
            desc='Recognizing entities (documents)')
        
        for i, filename in enumerate(input_files):
            doc_id = ''
            text = ''
            
            if filename_mode:
                doc_id = filename.strip(in_dir).strip('.txt')
               
                with open(filename, 'r') as input_file:
                    text = input_file.read()
                    input_file.close()
            
            else:
                text = filename
                doc_id = str(i)
            
            # Sentence segmentation
            doc_sentences = utils.sentence_splitter(text, lang_model)
            
            # Objectify input
            doc_obj = utils.objectify_ner_input(
                doc_id, text, doc_sentences)
            
            # Apply NER models to input text
            doc_entities = recognizer.apply(doc_obj)

            # Output recognized entities to a file
            # Prepare output string with annotations
            doc_annots = utils.prepare_output_from_objects(
                doc_entities, only_ner=True)

            out_filename = ''

            if out_dir == None:
                out_filename = '{}{}.ann'.format(tmp_out_dir, doc_id)                
                # Add Document object to Dataset object
                dataset.add_doc(doc_entities)

            else:
                out_filename = out_dir + doc_id + '.ann'

            with open(out_filename, 'w') as out_file:
                out_file.write(doc_annots[:-1])
                out_file.close()
            
            del doc_annots
            del text
            del doc_sentences
            del doc_obj
            del doc_entities
            
            utils.garbage_collect()

            pbar.update(1)
            
        pbar.close()

    del recognizer
    del lang_model
    del stopwords
    utils.garbage_collect()

    if out_dir == None:
        return dataset


def linker(
            recognize, types, nel_model, run_id, out_format=None, 
            ner_dir=None, out_dir=None, dataset=None):
    """Pipeline to perform Named Entity Linking. For each input 
    annotation files with recognized entities it outputs an updated 
    annotations file (BRAT format) with knowledge base identifiers for each
    entity.

    :param recognize: specifies wether the pipeline performs Named Entity 
        Recognition, defaults to False
    :type recognize: bool, optional
    :param types: types of entities to be recognized along with the respective
        target knowledge bases, defaults to {}. Options: 
        {'disease': 'medic'}, {'disease': 'do'}, 
        {'chemical': 'chebi'}, {'chemical': 'ctd_chem'},
        {'gene': 'ncbi_gene'},
        {'bioprocess': 'go_bp'},
        {'organism': 'ncbi_taxon'},
        {'anatomical': 'uberon'}, {'anatomical', 'ctd_anat'},
        {'cell_component': 'go_cc'},
        {'cell_line': 'cellosaurus'},
        {'cell_type': 'cell_ontology'},
        {'variant': ''}
        {<entity_type>: <custom_knowledge_base>}
    :type types: dict, optional
    :param nel_model: the Named Entity Linking model that will be used, 
        defaults to 'reel_nilinker'
    :param ner_dir: directory where the output of the NER stage is located. 
        Only applicable when there is already an output from the NER stage.
        Defaults to 'None'. 
    :type ner_dir: str, optional
    :param out_dir: path to directory where the output of the pipeline will be
        located, optional. If 'out_dir' == None (deafult) a Dataset object 
        including all documents and respective annotations will be returned  
    :type out_dir: str, defaults to None
    :param dataset: dataset (an object including all the input texts along with 
        the annotations from the NER stage), defaults to None
    :type dataset: Dataset, optional
    :raises ValueError: if 'ner_dir'==None and recognize==False, which means
        that if the NER stage was not performed it is necessary nevertheless
        indicate the directory containing annotation files corresponding to 
        the NER output
    """
    
    # Link the recognized/inputted entities to the specified KBs
    linker = nel(nel_model)
    target_kbs = {}
    
    for ent_type in types.keys():
        
        if types[ent_type] != '':
            target_kbs[ent_type] = types[ent_type]
    
    if recognize:
        
        if out_dir == None:
            ner_dir = '.tmp/{}/'.format(run_id)
        
        else:
            # The output of the previous NER step is locacted in the out_dir
            ner_dir = out_dir
    
    else:

        if ner_dir == None and run_id==None:
            raise ValueError('It is necessary to specify the directory \
                containing the NER output ("ner_dir")')
    
    nel_run_ids = linker.apply(target_kbs, ner_dir=ner_dir)
    
    del linker
    
    if out_dir == None:
        return utils.update_dataset_with_nel_output(dataset, nel_run_ids)
    
    else:
        utils.update_ner_file_with_nel_output(ner_dir, nel_run_ids, out_dir=out_dir)  


def annotate(recognize=False, link=False, types={}, input_text=None,
        in_dir=None, ner_dir=None, input_format='brat', out_format='brat',
        out_dir=None, ner_model='pubmedbert', nel_model='reel_nilinker'):
    """Pipeline to annotate text(s) with recognized entities (Named Entity and
    Recognition) to link them to knowledge base concepts (Named Entity Linking).

    :param recognize: specifies wether the pipeline performs Named Entity 
        Recognition, defaults to False
    :type recognize: bool, optional
    :param link: specifies wether the pipeline performs Named Entity 
        Linking, defaults to False
    :type link: bool, optional
    :param types: types of entities to be recognized along with the respective
        target knowledge bases, defaults to {}. Options: 
        {'disease': 'medic'}, {'disease': 'do'}, 
        {'chemical': 'chebi'}, {'chemical': 'ctd_chem'},
        {'gene': 'ncbi_gene'},
        {'bioprocess': 'go_bp'},
        {'organism': 'ncbi_taxon'},
        {'anatomical': 'uberon'}, {'anatomical', 'ctd_anat'},
        {'cell_component': 'go_cc'},
        {'cell_line': 'cellosaurus'},
        {'cell_type': 'cell_ontology'},
        {'variant': ''}
        {<entity_type>: <custom_knowledge_base>}
    :type types: dict, optional
    :param input_text: text string or list of text strings (each element 
        represinting a different document) to be annotated, defaults to None
    :type input_text: str or list, optional
    :param in_dir: path to directory containing text files to be annotated (NER
        and optionally NEL), 
        defaults to None
    :type in_dir: _type_, optional
    :param ner_dir: directory where the output of the NER stage is located. 
        Only applicable when there is already an output from the NER stage.
        Defaults to 'None'. 
    :type ner_dir: str, optional
    :param in_format: the format of the input files. Options: 'brat', 
        'bioc_xml', 'bioc_json', 'pubtator'
    :type input_format: str, optional, defaults to 'brat'
    :param out_dir: path to directory where the output of the pipeline will be
        located, optional. To choose current directory set out_dir==''.
        If 'out_dir' == None (deafult) a Dataset object 
        including all documents and respective annotations will be returned  
    :type out_dir: str, defaults to None
    :param out_format: the format of the ouput ('brat', None), defaults to None
    :type out_format: str, optional
    :param ner_model: the Named Entity Recognition model that will be used, 
        defaults to 'pubmedbert'
    :type ner_model: str, optional
    :param nel_model: the Named Entity Linking model that will be used, 
        defaults to 'reel_nilinker'
    :type nel_model: str, optional
    :raises ValueError: if both 'input_text' and 'in_dir' are None
    :raises ValueError: if both 'recognize' and 'link' are None
    :return: dataset (an object including all the input texts along with the 
        annotations) if 'out_dir' is None; an annotation file for each inputed
        text if 'out_dir' is different that None
    :rtype: Dataset object, text file(s)
    """
    run_id = ''.join(random.choices(string.ascii_uppercase + string.digits, 
        k=15)) 

    # Check if input arguments are valid
    utils.check_input_args(recognize, link, types, input_format,
        input_text, in_dir, ner_dir, out_dir, ner_model, nel_model)

    if ner_dir != None:
        in_dir = ner_dir
    
    if out_dir != None:
        
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
    
    #--------------------------------------------------------------------------
    #                   CONVERT INPUT TO THE BRAT FORMAT
    #-------------------------------------------------------------------------- 
    if input_text!= None:
        
        utils.convert_input_files(input_format, input_text=input_text, 
            in_dir=in_dir, recognize=recognize)
        
        in_dir += 'brat/'
        
    #--------------------------------------------------------------------------
    #                           NER
    #--------------------------------------------------------------------------
    if recognize:
        entity_types = types.keys()

        if out_dir != None:
            recognizer(
                in_dir, input_text, entity_types, out_dir, ner_model, run_id)
        
        else:
            dataset = recognizer(
                in_dir, input_text, entity_types, out_dir, ner_model, run_id)
    #--------------------------------------------------------------------------
    #                           NEL
    #--------------------------------------------------------------------------
    if link:

        if out_dir != None:
            linker(
                recognize, types, nel_model, run_id, out_format=out_format,
                    ner_dir=in_dir, 
                out_dir=out_dir)

        else:
            dataset = linker(
                recognize, types, nel_model, run_id, out_format=out_format, 
                ner_dir=in_dir, dataset=dataset, out_dir=out_dir)
            
            return dataset