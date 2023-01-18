#!/usr/bin/env python
"""
Classes that are the backbone of the package.
Logical hierarchy: Entity -> Sentence -> Document -> Dataset
"""


class Entity:
    """Represent a given recognized entity and its respective information."""
    __slots__ = ['start', 'end', 'text', 'type', 'kb_id', 'score',  'sent_num']
    def __init__(self, start, end, text, ent_type, kb_id, score, sent_num):
        # The spans (start, end) are defined according to the entire of text 
        # and not relative to the sentence where they are present
        self.start = start 
        self.end = end
        self.text = text
        self.type = ent_type
        self.kb_id = kb_id
        self.score = score
        self.sent_num = sent_num
    
    def set_kb_id(self, kb_id):
        
        self.kb_id = kb_id


class Sentence():
    """Sentence including a text and (optionally) 1 or more recognized 
    entities"""
    __slots__ = ['start', 'end', 'text', 'entities', 'num']
    def __init__(self, start, end, text):

        self.start = start
        self.end = end
        self.text = text
        self.entities = []
        self.num = 0 # Sentence number in the context of the document
    
    def set_num(self, num):
        
        self.num = num

    def add_entity(self, Entity):
        
        self.entities.append(Entity)
    
    def add_multi_entities(self, entities):
        
        self.entities.extend(entities)

    def update_entity(self, entity_to_up):

        entity_pos = int()

        for i, entity in enumerate(self.entities):
            
            if entity.text == entity_to_up.text \
                    and (entity.start == entity_to_up.start) \
                    and (entity.end == entity_to_up.end):

                entity_pos = i
        
        self.entities.pop(entity_pos)
        self.entities.insert(entity_pos, entity_to_up)

    def remove_entity(self, entity):

        if entity in self.entities:
            self.entities.remove(entity)


class Document():
    """Set with 1 or more sentences."""
    
    __slots__ = ['text', 'sentences', 'entities', 'length', 'num_sents', 'id']
    def __init__(self, text):

        self.text = text 
        self.sentences = []
        self.entities = []
        self.length = len(text)
        self.num_sents = 0
        self.id = None 

    def set_id(self, id):

        assert type(id) == str, 'Invalid type for document ID'
        self.id = id

    def get_sentence(self, sentence_pos):
        return self.sentences[sentence_pos]

    def add_sentence(self, sentence):
        
        self.sentences.append(sentence)
        self.entities.extend(sentence.entities)
    
    def add_sentence_in_specific_pos(self, sentence, sentence_pos):
        
        self.sentences.insert(sentence_pos, sentence)
    
    def remove_sentence_in_specific_pos(self, sentence_pos):
        
        if sentence_pos < len(self.sentences):
            self.sentences.pop(sentence_pos)

    def add_multi_sentences(self, sentences):
        
        self.sentences.extend(sentences)

        for sent in sentences:
            self.entities.extend(sent.entities)
    
    def update_sentence(self, sent_up, sent_num):
        
        self.remove_sentence_in_specific_pos(sent_num)
        self.add_sentence_in_specific_pos(sent_up, sent_num)
        
        # Update the entities associated with the inputed sentence
        self.entities = []

        for sent in self.sentences:
            self.entities.extend(sent.entities)

    def add_entities(self, entities2add):
        """entities2add is a list containing 1 or more Entity objects 
        associated with current document."""

        self.entities.extend(entities2add)
    
    def remove_entities(self, entities2remove):
        
        for entity in entities2remove:
            
            if entity in self.entities:
                self.entities.remove(entity)

    def remove_all_entities(self):
        self.entities = []


class Dataset():
    """Collection of 1 or more documents."""

    __slots__ = ['documents', 'num_docs', 'doc_ids']
    def __init__(self):

        self.documents = []
        self.num_docs = 0
        self.doc_ids = []

    def ____str__(self):

        outstr = ''
        
        for doc in self.documents:
            outstr += doc.id + '\n'

        return outstr

    def set_name(self, name):
        
        self.name = name

    def add_doc(self, document):
        """'document' is a Document object."""

        self.documents.append(document)
        self.doc_ids.append(document.id)
        self.num_docs += 1

    def add_multi_doc(self, docs):
        """'docs' is a list containing more than 1 Document objects."""

        self.documents.extend(docs)
        doc_ids_2_add = [doc.id for doc in docs]
        self.doc_ids.extend(doc_ids_2_add)
        self.num_docs += len(docs)

    def update_doc(self, doc_up, doc_id):
        """'doc_up' is the updated Document object that will replace the old 
        Document object represented by 'doc_id'."""

        old_doc_index = self.doc_ids.index(doc_id)
        self.documents.pop(old_doc_index)
        self.documents.insert(old_doc_index, doc_up)

    def filter_by_type(self, entity_type):
        """Filter entities in the document by their type. returns dataset 
        object with only entities of given type
        """
        
        dataset_up = Dataset()

        for doc in self.documents:
            doc_up = doc
            doc_up.remove_all_entities()
            
            for sent in doc_up.sentences:
                
                for entity in sent.entities:

                    if entity.type == entity_type:
                        sent.add_entity(entity)
            
            dataset_up.add_doc(doc_up)

        return dataset_up