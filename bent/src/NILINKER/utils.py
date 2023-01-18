#!/usr/bin/env python

import bent.src.cfg as cfg
import orjson as json
import numpy as np
from rapidfuzz import process, fuzz


class WordConcept:
    """Class representing a word-concept (WC) dictionary object associated with 
    a given KB. It includes mappings between words and WC int ids, words and 
    candidates, etc.
    """
    
    __slots__ = ['partition', 'filepath', 'word2candidates', 'word2id',
        'id2word', 'candidate_num', 'candidate2id', 'id2candidate', 
        'root_concept_int' ]
    def __init__(self, partition):
    
        self.partition = partition
        self.filepath = "{}data/NILINKER/word_concept/wc_{}.json".format(cfg.root_path, partition)
        self.word2candidates = None
        self.word2id = None
        self.id2word = None
        self.candidate_num = None
        self.candidate2id = None
        self.id2candidate = None
        self.root_concept_int = None
        
    def build(self):
        """Fill a WordConcept object with info about words belonging to 
        the considered Word-Concept (WC) dict, and candidates and respectives 
        int ids. (*note: Candidate int ids are distinct from WC words ids). 
        """

        # Load node_id_to_int
        with open(
                "{}data/NILINKER/embeddings/{}/node_id_to_int_{}.json"\
                .format(cfg.root_path, self.partition, self.partition)) as in_file:
            node_id_to_int = json.loads(in_file.read())

        # Create candidate2id and id2candidate
        id2candidate, candidate2id = {}, {}
        
        for concept in node_id_to_int.keys():
            candidate_int = node_id_to_int[concept]
            candidate2id[concept] = candidate_int 
            id2candidate[candidate_int] = concept

        # Add int for the root concept to wc
        root_dict = {"go_bp": ("GO:0008150", "biological_process"), 
                    "chebi": ("CHEBI:00", "root"), 
                    "hp": ("HP:0000001", "All"), 
                    "medic": ("MESH:C", "Diseases"), 
                    "ctd_anat": ("MESH:A", "Anatomy"), 
                    "ctd_chem": ("MESH:D", "Chemicals")}
        root_concept_kb_id= root_dict[self.partition][0]
        root_concept_int = candidate2id[root_concept_kb_id]
        self.root_concept_int = root_concept_int

        word2candidates = {}
        
        # Load word-concept file into dict
        with open(self.filepath, 'r', encoding='utf-8') as wc: 
            word2candidates = json.loads(wc.read())
        
        # Create word2candidates with candidates int
        vocab_size = len(node_id_to_int.keys())
        
        word2candidates_up, wc_word2id, id2word = {}, {}, {}
        word_count = 0

        for word in word2candidates.keys():
            word_count += 1
            wc_word2id[word] = word_count
            id2word[word_count] = word

            candidates = word2candidates[word]
            candidates_int = []
            
            for candidate in candidates:
                # Convert concept ID in int
                candidate_int = node_id_to_int[candidate]
                candidate_int_up = 0

                if candidate_int == vocab_size:
                    candidate_int_up = root_concept_int

                else:
                    candidate_int_up = candidate_int
                
                candidates_int.append(candidate_int_up)

            word2candidates_up[word] = candidates_int
            
        self.word2candidates = word2candidates_up
        self.word2id = wc_word2id 
        self.id2word = id2word
        self.candidate2id = candidate2id
        self.id2candidate = id2candidate
        self.candidate_num = len(candidate2id.keys())
        root_concept_kb_id= root_dict[self.partition][0]
        root_concept_int = candidate2id[root_concept_kb_id]
        self.root_concept_int = root_concept_int
        
    
def load_word_embeds(embeds_dir):
    """Load word embeddings from file into a Numpy array and generate dicts 
    with information about each word and respective int ID.

    :param embeds_filepath: path for the file containing word embeddings
    :type embeds_filepath: str
    :return: embeds, word2id, id2word
    :rtype: Numpy array, dict, dict
    """

    embeds, vocabulary = [], []

    with open(embeds_dir + 'word_embeddings.txt', 'r', encoding='utf-8') \
            as embed_file:
        
        for line in embed_file.readlines():
            word = line.split()[0]
            embed = [float(item) for item in line.split()[1:]]
            embeds.append(embed)
            vocabulary.append(word)
        
        embed_file.close()
    
    assert (len(embeds) == len(vocabulary))

    embeds_word2id = {}
    
    with open(embeds_dir + 'word2id.json', 'r') as word2id_file:
        embeds_word2id = json.loads(word2id_file.read())
        word2id_file.close()
 
    embeds = np.array(embeds)#s.astype('float32')
    embeds = embeds / np.sqrt(np.sum(embeds * embeds, axis=1, keepdims=True))
   
    return embeds, embeds_word2id


def load_candidate_embeds(embeds_filepath, candidate2id):
    """Load candidate embeddings from file into a Numpy array.

    :param embeds_filepath: path for the file containing candidate 
        (i.e. KB concepts) embeddings
    :type embeds_filepath: str
    :param candidate2id: info about candidates and respective internal ID
    :type candidate2id: dict
    :return: embeds
    :rtype: Numpy array
    """

    embed_dict = {}
    
    with open(embeds_filepath, 'r', encoding='utf-8') as embed_file:
        
        for line in embed_file.readlines():
            word = line.split()[0]
            embedding = [float(item) for item in line.split()[1:]]
            embed_dict[word] = embedding

    embeds = []
    
    for candidate in candidate2id.keys(): 
        candidate_id = candidate2id[candidate]
        embeds.append(embed_dict[str(candidate_id)])
    
    embeds = np.array(embeds)
    embeds = embeds / np.sqrt(np.sum(embeds * embeds, axis=1, keepdims=True))
    
    return embeds


def get_candidates_4_word(
        wc_2idword, word2candidates, word_str='', wc_word_id=-1):
    """Retrieve KB candidate concepts for given word (either WC word id or 
    string) or for the most similar word in the WC if the word is not present 
    in the WC.

    :param wc_2idword: mappings between WC word ids and WC words
    :type wc_2idword: dict
    :param word2candidates: mappings between WC words and KB 
        candidate concepts
    :type word2candidates: dict
    :param word_str: string of the target word
    :type word_str = str
    :param wc_word_id: the WC word id for the target word 
    :type wc_word_id: int or numpy.int64
    :raises ValueError: if given input is invalid, input must be either a 
        string or a valid WC word id
    :return: candidates_ids
    :rtype: Numpy array

    >>> wc_word_id = 444
    >>> wc_2idword = {444: 'gene'}
    >>> word2candidates = {'gene': [1, 2, 3]}
    >>> get_candidates_4_wordid(wc_2idword,word2candidates,word_id=wc_word_id)
    [1, 2, 3]
    >>> word = 'gene'
    >>> get_candidates_4_wordid(wc_2idword,word2candidates,word_str=word)
    [1, 2, 3]
    >>> word_id = 3.5
    >>> get_candidates_4_wordid(wc_2idword,word2candidates,word_id=word_id)
    ValuError: 'Input not valid! Must be either a word string or a WC word id'
    """

    word = ''
    
    if wc_word_id != -1 and \
            (type(wc_word_id) == np.int64 or type(wc_word_id) == int):
        
        word = wc_2idword[wc_word_id]
        
    else:

        if word_str != '':
            word = word_str
        
        else:
            raise ValueError(
               'Input not valid! Must be either a word string or a WC word id')
    
    candidates = []

    if word in word2candidates.keys():
        candidates = word2candidates[word]

    else:
        top_match = process.extract(
                        word, word2candidates.keys(), 
                        scorer=fuzz.token_sort_ratio, 
                        limit=1)
        most_similar_word = top_match[0][0]
        candidates = word2candidates[most_similar_word]

    candidates_ids = np.array(candidates)
    
    return candidates_ids

   
def get_wc_embeds(partition):
    """Create and populate WordConcept object and get Numpy arrays with 
    candidate and word embeddings.

    :param partition: has value 'medic', 'ctd_chem', 'hp', 'chebi', 'go_bp', 
        'ctd_anat'
    :type partition: str
    :return: word_embeds, candidate_embeds, wc
    :rtype: Numpy array, Numpy array, WordConcept object
    """

    embeds_dir = "{}data/NILINKER/embeddings/{}/".format(cfg.root_path, partition)
    word_embeds_filepath = embeds_dir 
    candidates_embeds_filepath = embeds_dir + partition + ".emb"

    wc = WordConcept(partition)
    wc.build()

    word_embeds, embeds_word2id = load_word_embeds(word_embeds_filepath)
    
    candidate_embeds = load_candidate_embeds(
                            candidates_embeds_filepath, 
                            wc.candidate2id)

    return word_embeds, candidate_embeds, wc, embeds_word2id


def get_tokens_4_entity(entity_str):
    
    tokens = []
    
    if type(entity_str) == str: 
        tokens = entity_str.split(" ")
    
    else:
        raise TypeError('Entity type is not <str>')

    if len(tokens) == 1:
        # If the entity has only 1 word, we assume that 
        # it has two repeated words
        tokens = [tokens[0], tokens[0]]

    return tokens


def get_words_ids_4_entity(
        entity_str, wc_word2id={}, embeds_word2id={}, mode=''):
    """Tokenize given entity string and, according with the selected mode,
    return the ids of the words that are part of the entity. If mode 'wc' it 
    returns the WC word ids for left and right words, if mode 'embeds' it 
    returns the embeddings word ids for left and right words. If a given word 
    is not present in the given dictionary, it finds the most similar word in 
    the dict according with the Levenshtein distance.
    
    :param entity_str: the target entity string
    :type entity_str: str
    :param wc_word2id: mappings between each word in the WC and the
        respective int ids
    :type wc_word2id: dict
    :param embeds_word2id: mappings between each word in the embeddings
        vocabulary and the respective int ids
    :type embeds_word2id: dict
    :raise ValueError: if the given mode is invalid, mode must be either 'wc'
        or 'embeds'
    :return: word_l_id and word_r_id including the word ids of the left and
        right words of the given entity.
    :rtype: tuple with 2 ints

    >>> entity = 'arrythmic palpitation'
    >>> wc_word2id = {'palpitation':1663,'arrythmic':1629,'hematoma':1353}
    >>> get_words_ids_4_entity(entity, wc_word2id=wc_word2id, mode='wc')
    1629, 1663
    
    >>> entity = 'arrythmic palpitations'
    >>> embeds_word2id = {'palpitation':1,'arrythmic':2,'hematoma':3}
    >>> mode = 'embeds'
    >>> get_words_ids_4_entity(entity,embeds_word2id=embeds_word2id,mode=mode)
    2, 1
    """
    
    ids = {}

    if mode == 'wc':
        ids = wc_word2id
    
    elif mode == 'embeds':
        ids = embeds_word2id

    else:
        raise ValueError('Invalid mode! Choose either "wc" (to get the \
                          word ids from Word-Concept) or "embeds" mode \
                         (to get words ids from the embeddings vocabulary)')

    tokens = get_tokens_4_entity(entity_str)

    word_l_id, word_r_id, token_count = 0, 0, 1
    
    for token in tokens[:2]:
        # Only consider the first two words of the entity
        
        if token in ids.keys():

            if token_count == 1:
                word_l_id = ids[token]

            elif token_count == 2:
                word_r_id = ids[token]

        else:
            top_match = process.extract(
                token, ids.keys(), scorer=fuzz.token_sort_ratio, 
                limit=1)
           
            most_similar_word = ids[top_match[0][0]]
            
            if token_count == 1:
                word_l_id = most_similar_word

            elif token_count == 2:
                word_r_id = most_similar_word
        
        token_count += 1
    
    return word_l_id, word_r_id


def get_kb_data(partition):
    """Load KB data (concept names, synonyms, IDs, etc) associated with given 
    partition into a KnowledgeBase object.

    :param partition: has value 'medic', 'ctd_chem', 'hp', 'chebi', 
        'go_bp' or 'ctd_anat'
    :type partition: str
    :return: kb_data representing the given KB
    :rtype: KnowledgeBase object
    """

    source_filename = '{}data/dicts/{}/id_to_name.json'.format(cfg.root_path, partition)

    if partition == 'chebi':
        source_filename = '{}data/dicts/chebi/id_to_name_nilinker.json'.format(cfg.root_path)

    with open(source_filename, 'r') as in_file:
        id_to_name = json.loads(in_file.read()) 
        in_file.close()

    # Format the KB identifiers (MESH:D019967 passa a MESH_D019967)
    id_to_name_up = {}

    for kb_id in id_to_name.keys():
        kb_id_up = kb_id.replace('_', ':')
        id_to_name_up[kb_id_up] = id_to_name[kb_id]

    return id_to_name_up
