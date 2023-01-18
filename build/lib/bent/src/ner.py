#!/usr/bin/env python
import bent.src.cfg as cfg
import gc
import orjson as json
import os
import bent.src.utils  as utils
from transformers import AutoModelForTokenClassification, AutoTokenizer, TokenClassificationPipeline


class ner():
    """Represent a Named Entity Recognition (NER) pipeline"""
    
    __slots__= ['name', 'stopwords', 'module_root_path', 'model_type', 'models', 
        'disease_prob', 'chemical_prob', 'gene_prob', 'organism_prob',
        'bioprocess_prob', 'anatomical_prob', 'cell_component_prob',
        'cell_line_prob', 'variant_prob']
    def __init__(self, name, types, stopwords):
        """_summary_

        :param name: the name of the model that will be loaded
        :type name: str
        :param types: the entity types that will be recognized 
        :type types: list
        :param stopwords: frequent words ('the', 'and', 'of) that will not be 
            considered as an entity
        :type stopwords: str
        :raises ValueError: if the inputted model name is not 'pubmedbert'
        """
        self.name = name    
        self.stopwords = stopwords

        module_root_path = cfg.root_path
        self.module_root_path = module_root_path
        #--------------------------------------------------------------------
        # Load NER models and dictionaries with entities probabilities to 
        # resolve overlapping entities
        #--------------------------------------------------------------------
        self.model_type = None
        self.models = {}
      
        if self.name == 'pubmedbert':
            self.model_type = 'bert'
            
            if 'disease' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Disease"
                self.models['disease'] = ner.load_transformer_model(model_name)
                dict_filename = '{}data/overlapping_entities/disease.json'.format(module_root_path)
                if len(types) > 1:
                    self.disease_prob = ner.load_probabilities_file(dict_filename)
                
            if 'chemical' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Chemical"
                self.models['chemical'] = ner.load_transformer_model(model_name)
                dict_filename = '{}data/overlapping_entities/chemical.json'.format(module_root_path)
                if len(types) > 1:
                    self.chemical_prob = ner.load_probabilities_file(dict_filename)
           
            if 'gene' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Gene"
                self.models['gene'] = ner.load_transformer_model(model_name)
                dict_filename = '{}/data/overlapping_entities/gene.json'.format(module_root_path)
                if len(types) > 1:
                    self.gene_prob = ner.load_probabilities_file(dict_filename)

            if 'organism' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Organism"
                self.models['organism'] = ner.load_transformer_model(model_name)
                dict_filename = '{}data/overlapping_entities/organism.json'.format(module_root_path)
                if len(types) > 1:    
                    self.organism_prob = ner.load_probabilities_file(dict_filename)

            if 'bioprocess' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Bioprocess"
                self.models['bioprocess'] = ner.load_transformer_model(model_name)   
                dict_filename = '{}data/overlapping_entities/bioprocess.json'.format(module_root_path)
                if len(types) > 1:    
                    self.bioprocess_prob = ner.load_probabilities_file(dict_filename)

            if 'anatomical' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Anatomical"
                self.models['anatomical'] = ner.load_transformer_model(model_name)   
                dict_filename = '{}data/overlapping_entities/anatomical.json'.format(module_root_path)
                if len(types) > 1:    
                    self.anatomical_prob = ner.load_probabilities_file(dict_filename)
            
            if 'cell_component' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Cell-Component"
                self.models['cell_component'] = ner.load_transformer_model(model_name)   
                dict_filename = '{}data/overlapping_entities/cell_component.json'.format(module_root_path)
                if len(types) > 1:    
                    self.cell_component_prob = ner.load_probabilities_file(dict_filename)
            
            if 'cell_line' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Cell-Line"
                self.models['cell_line'] = ner.load_transformer_model(model_name)   
                dict_filename = '{}data/overlapping_entities/cell_line.json'.format(module_root_path)
                if len(types) > 1:    
                    self.cell_line_prob = ner.load_probabilities_file(dict_filename)
            
            if 'cell_type' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Cell-Type"
                self.models['cell_type'] = ner.load_transformer_model(model_name)   
                dict_filename = '{}data/overlapping_entities/cell_type.json'.format(module_root_path)
                if len(types) > 1:    
                    self.cell_type_prob = ner.load_probabilities_file(dict_filename)

            if 'variant' in types:
                model_name = "pruas/BENT-PubMedBERT-NER-Variant"
                self.models['variant'] = ner.load_transformer_model(model_name)   
                dict_filename = '{}data/overlapping_entities/variant.json'.format(module_root_path)
                if len(types) > 1:    
                    self.variant_prob = ner.load_probabilities_file(dict_filename)  
        
        else:
            raise ValueError('Model not implemented!')

    @staticmethod
    def load_transformer_model(model_filepath):
        """Load NER model from given filepath into a 
        'TokenClassificationPipeline' object (Hugging Face library) ready to 
        annotate texts.

        :param model_filepath: local or online path for the model
        :type model_filepath: str
        :return: loaded_model
        :rtype: 'TokenClassificationPipeline' object
        """
        
        
        model = AutoModelForTokenClassification.from_pretrained(model_filepath)
        tokenizer_1 = AutoTokenizer.from_pretrained(
            model_filepath, model_max_length=512)
        loaded_model = TokenClassificationPipeline(task='ner', 
                        model=model, 
                        tokenizer=tokenizer_1,
                        aggregation_strategy='simple')#, 
                        #grouped_entities=True)#,
                        #aggregation_strategy='simple')
        
        return loaded_model
    
    @staticmethod
    def load_probabilities_file(dict_filename):
        
        type_dict = {}

        if os.path.exists(dict_filename):
            with open(dict_filename, 'r') as dict_file:
                type_dict = json.loads(dict_file.read())
                dict_file.close()
        
        return type_dict
 
    @staticmethod
    def correct_tokens(sent, raw_annots, entity_type, stopwords):
        """Correct the output of BERT-based models by grouping tokens 
        associated with the same entity. For example, the entities
        'Am' and '##minoacids' are considered independent, but they are 
        the same entity.

        :param sent: specific sentence where the model was applied 
        :type sent: 'Sentence' object
        :param raw_annots: recognized entities in given sentence
        :type raw_anots: list
        :param entity_type: the type of the entities that were recognized in 
            this sentence
        :type entity_type: str
        :param stopwords: frequent words ('the', 'and', 'of) that will not be 
            considered as an entity
        :type stopwords: str
        :return: corrected_annots including the recognized entities with text 
            and span corrected
        :rtype: list
        """
        
        annots_up = []
        token_count = 0
        
        for i, annot in enumerate(raw_annots):
            current_start = sent.start + annot['start']
            current_end =  sent.start + annot['end']
            current_token_score = annot['score']
            
            if i > 0:
                previous_annot = annots_up[-1]
                previous_start = previous_annot[0]
                previous_end = previous_annot[1]
                previous_token_score = previous_annot[4]
                previous_token_count = previous_annot[5]
                   
                if previous_end == (current_start - 1) \
                        or previous_end == (current_start):
                   
                    # Entity spans are defined in the context of the sentence 
                    # and not of the entire document
                    start_tmp = previous_start - sent.start
                    end_tmp = current_end - sent.start
                    entity_text_up = sent.text[start_tmp:end_tmp]
                    
                    # Calculate averaget of previous token scores with current
                    # one. Formula: ( n * a + v ) / (n + 1);
                    current_token_count_update = previous_token_count + 1
                    current_token_score_updated = (previous_token_count * \
                        previous_token_score + current_token_score) / \
                        (current_token_count_update)
                    
                    annot_up = [
                        previous_start, current_end, 
                        entity_text_up, entity_type, \
                        current_token_score_updated, current_token_count_update]
                    
                    annots_up.append(annot_up)

                    # Delete previous incomplete annotation and replace it 
                    # by the updated entity
                    del annots_up[-2]
                    
                else:
                    # Current entity is a new entity
                    start_tmp = current_start - sent.start
                    end_tmp = current_end - sent.start
                    entity_text = sent.text[start_tmp:end_tmp]
                    current_token_count = 1
                    
                    annot_up = [
                        current_start, current_end, 
                        entity_text, entity_type, 
                        current_token_score, current_token_count]
                    
                    annots_up.append(annot_up)
                
            else:
                # Current entity is the first entity in given sentence
                start_tmp = current_start - sent.start
                end_tmp = current_end - sent.start
                entity_text = sent.text[start_tmp:end_tmp]
                token_count += 1
                            
                annot_up = [
                    current_start, current_end,
                    entity_text, entity_type, current_token_score, token_count]

                annots_up.append(annot_up)
        
        # Further post_processing of the entities
        corrected_annots = []

        for annot in annots_up:
            text = annot[2]
            words = text.split(' ')

            if text[0] != ':':

                # Do not consider entities with length=1 except of chemical type
                if len(text) == 1:

                    if entity_type == "ChemicalEntity":
                        # Chemical entities can have length 1 (e.g. chemical 
                        # elements) but there can be errors (e.g. "-"")
                        
                        if text.isalpha() and text not in stopwords:
                            # The only char is not a letter, so it cannot be a 
                            # chemical element
                            corrected_annots.append(annot)
                        
                elif len(text) > 1:
                    
                    if len(words) > 1:
                        corrected_annots.append(annot)
                    
                    elif len(words) == 1:
                        
                        # If the entity has only 1 word and that word is a stop 
                        # word, the entity won't be considered
                        if text not in stopwords:
                            corrected_annots.append(annot)
                
                if '\n' in text:
                    # Correct error such as 'fenofibrate\nFenofibrate'
                    # Current annotation will origin two distinct annotations 
                    text1 = text.split('\n')[0]
                    start1 = annot[0]
                    end1 = start1 + len(text1)
                    annot1 = [start1, end1, text1, annot[3], annot[4], annot[5]]
                    
                    text2 = text.split('\n')[1]
                    start2 = end1 + 1
                    end2 = start2 + len(text2) 
                    annot2 = [start2, end2, text2, annot[3], annot[4], annot[5]]

                    # Replace current annotation with annotation 1
                    current_index = corrected_annots.index(annot)
                    corrected_annots[current_index] = annot1

                    # Insert annotation 2 after annotation 1
                    index_2 = current_index + 1
                    corrected_annots.insert(index_2, annot2)

        return corrected_annots

    def get_entity_prob(self, ent_text, ent_type):
    
        target_dict = {}

        if ent_type == 'disease':
            target_dict = self.disease_prob

        if ent_type == 'chemical':
            target_dict = self.chemical_prob

        if ent_type == 'gene':
            target_dict = self.gene_prob

        if ent_type == 'organism':
            target_dict = self.organism_prob

        if ent_type == 'bioprocess':
            target_dict = self.bioprocess_prob

        if ent_type == 'anatomical':
            target_dict = self.anatomical_prob

        if ent_type == 'cell_component':
            target_dict = self.cell_component_prob

        if ent_type == 'cell_line':
            target_dict = self.cell_line_prob

        if ent_type == 'cell_type':
            target_dict = self.cell_type_prob

        if ent_type == 'variant':
            target_dict = self.variant_prob

        prob = 0.0

        if ent_text.lower() in target_dict.keys():
            prob = target_dict[ent_text.lower()]
        
        return prob
    
    def compare_entities_w_same_text(self, annot, annot2, entity_frequency):

        # Retrieve probabilities from external dicts         
        annot_prob = ner.get_entity_prob(self, annot.text, annot.type)
        annot2_prob = ner.get_entity_prob(self, annot2.text, annot2.type)

        #--------------------------------------------------------------------
        # Remove the entity with lower probability
        entity2keep = None
        entity2remove = None

        if annot_prob > annot2_prob:
            entity2remove = annot2
            entity2keep = annot
        
        elif annot_prob < annot2_prob:
            entity2remove = annot
            entity2keep = annot2
        
        elif annot_prob == annot2_prob:
            annot_key = annot.text + '_' + annot.type
            freq1 = entity_frequency[annot_key]
            annot2_key = annot2.text + '_' + annot2.type
            freq2 = entity_frequency[annot2_key]

            if freq1 > freq2:
                entity2remove = annot2
                entity2keep = annot

            elif freq1 < freq2:
                entity2remove = annot
                entity2keep = annot2

        return entity2keep, entity2remove

    @staticmethod
    def get_entity_frequency_in_doc(entities):

        entity_frequency = {}

        for entity in entities:
            entity_key = entity.text + '_' + entity.type

            if entity.text in entity_frequency.keys():
                entity_frequency[entity_key] += 1
        
            else:
                entity_frequency[entity_key] = 1
        
        return entity_frequency

    def correct_overlapping_annotations(self, doc):
        """Correct overlapping entities in a given document. The overlapping
        is both at the level of span (two entities share either the start or 
        the end position in a given sentence) and at the level of the string 
        (two entities with the same string classified according different 
        entities types)

        :param doc:
        :type doc: Document object
        :return: doc
        :rtype: 
        """

        #---------------------------------------------------------------------
        # Resolve overlapping pairs of entities in each sentence of given doc
        #---------------------------------------------------------------------

        # Get frequency of each entity
        entity_frequency = ner.get_entity_frequency_in_doc(doc.entities)

        #---------------------------------------------------------------------  
        # Resolve entities that have the same text, different entity type and
        # that are located in DIFFERENT SENTENCES of the document
        #---------------------------------------------------------------------     
        doc_entities = doc.entities

        for annot in doc_entities:
            
            for annot2 in doc_entities:

                if annot.text == annot2.text and \
                    annot.type != annot2.type:

                    entity2keep, entity2remove = ner.compare_entities_w_same_text(
                        self, annot, annot2, entity_frequency)

                    if entity2keep != None and entity2remove != None:
                        sent = doc.get_sentence(entity2remove.sent_num)
                        sent.remove_entity(entity2remove)
                        doc.remove_entities([entity2remove])

                        # Change the type of the deleted entity and add it again
                        entity2add = entity2remove
                        entity2add.type = entity2keep.type
                        sent.add_entity(entity2add)
                        doc.update_sentence(sent, sent.num)

        return doc
        
    def apply(self, document):
        """Annotate the texts belonging to given collection with the previously
        loaded model(s).

        :param document: doc_obj including all the information about the input 
            text, such as its identifier and its sentences 
        :type document: Document object
        :raises ValueError: if the loaded model has different type that 'bert'
        :return: doc_entities including the inputted information updated with
            the recognized entities
        :rtype: Document object
        """

        if self.model_type == 'bert':
            doc_sentences = document.sentences
            
            for i, sent in enumerate(doc_sentences):
                
                for model in self.models:
                    raw_annots = self.models[model](
                        sent.text, padding=True, truncation=True)
                    annots_up = ner.correct_tokens(
                        sent, raw_annots, model, self.stopwords)

                    annots_obj = utils.objectify_entities(annots_up, i)
                    
                    sent.add_multi_entities(annots_obj)
                    document.update_sentence(sent, i)
                        
            doc_entities = ner.correct_overlapping_annotations(self, document)

            del doc_sentences
            del raw_annots
            del annots_up 
            del annots_obj
            utils.garbage_collect()

        else:
            raise ValueError('Model not implemented!')

        return doc_entities
