#!/usr/bin/env python
from bent.src.abbreviation_detector.run import run_Ab3P
from bent.src.REEL.run import run
from tqdm import tqdm


class nel():
    """Represent a Named Entity Linking (NEL) pipeline"""
    __slots__ = ['model']
    def __init__(self, model):
        self.model = model
    
    def apply(self, target_kbs, ner_dir=None):
        """Link or normalise input entities to target knwoledge bases using 
        the previously specified model.

        :param in_dir: path to the directory including the texts of the 
            documents where the entities were recognized
        :type in_dir: str
        :param ner_dir: path to directory where the recognized entities are
            stored in the annotations files
        :type ner_dir: str
        :param target_kbs: the entity types and the respective knowledge bases
            to where the recognized entities will be linked
        :type target_kbs: dict
        :raises ValueError: if the selected model is different than 'reel2'
        :return: nel_runs including the run ids (for each target knowledge base
            is generated a distinct run id) associated with the application of 
            the mode
        :rtype: list
        """
        
        nel_runs = []
        pbar = tqdm(total=len(target_kbs.keys()), colour= 'green', 
            desc='Linking entities (knowledge bases)')
        
        if self.model == 'reel_nilinker':
        
            # ----------------------------------------------------------------
            # Get abbreviations with AB3P in each document of the dataset
            # ----------------------------------------------------------------
            abbreviations = run_Ab3P(ner_dir) # CHeck if runs with NER_DIR specified 
          
            # ----------------------------------------------------------------
            #Sequentially link entities to the respective target knowledge base
            # ----------------------------------------------------------------
            for ent_type in target_kbs.keys():
                kb = target_kbs[ent_type]
                
                # Run REEL
                nel_run_name = run(ner_dir, kb, ent_type, abbreviations)
                nel_runs.append(nel_run_name)
                
                pbar.update(1)
            
            pbar.close()
        
        else:
            raise ValueError('Model not implemented!')
        
        return nel_runs