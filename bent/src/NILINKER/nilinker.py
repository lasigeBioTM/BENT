#!/usr/bin/env python

import numpy as np
import tensorflow as tf
from bent.src.NILINKER.utils import get_candidates_4_word, get_words_ids_4_entity


class Words2embed(tf.keras.layers.Layer):
    """First layer of the model, encodes entities and 
       candidates with embeddings."""
    
    def __init__(self, wc, word_embeds, candidate_embeds):
        super(Words2embed, self).__init__()
        self.word_embeds = word_embeds
        self.candidate_embeds = candidate_embeds
        self.wc_word2id = wc.word2id
        self.id2word = wc.id2word
        self.word2candidates = wc.word2candidates
        self.root_concept_int = wc.root_concept_int
    
    def call(self, entity):

        # To get candidates for word l and r, we use the WC word_ids
        wc_word_l_id = entity.numpy()[0]
        wc_word_r_id = entity.numpy()[1]

        input_candidates_l = get_candidates_4_word(
                                self.id2word, 
                                self.word2candidates,
                                wc_word_id=wc_word_l_id)
        
        input_candidates_r = get_candidates_4_word(
                                self.id2word, 
                                self.word2candidates,
                                wc_word_id=wc_word_r_id)
        
        embed_candidates_r = tf.nn.embedding_lookup(
            params=self.candidate_embeds, ids=input_candidates_r)
        embed_candidates_l = tf.nn.embedding_lookup(
            params=self.candidate_embeds, ids=input_candidates_l)

        # To get the embeddings for word l and r, we use the embeds word ids
        embeds_word_l_id = entity.numpy()[2]
        embeds_word_r_id = entity.numpy()[3]

        input_l = np.array([embeds_word_l_id, ])
        input_r = np.array([embeds_word_r_id, ])
        
        embed_word_l = tf.nn.embedding_lookup(
            params=self.word_embeds, ids=input_l)
        embed_word_r = tf.nn.embedding_lookup(
            params=self.word_embeds, ids=input_r)
       
        return embed_word_l, embed_word_r, \
               embed_candidates_l, embed_candidates_r 


class Attention(tf.keras.layers.Layer):
    """Attention layer of the model."""

    def __init__(self, params):
        super(Attention, self).__init__()
        
        self.W_a = tf.Variable(
            tf.random.truncated_normal([params[0], params[0]], \
            stddev=0.5), 
            tf.float32, name='W_a')
        
        self.b_a = tf.Variable(
            tf.zeros([1, params[0]]), tf.float32, name='b_a')

    @staticmethod
    def determine_attention(
            direction, embed_word, embed_opposite_candidates, W_a, b_a):
        
        direction_dict = {"l": "r", "r": "l"}
        name1 = "embed_align_" + direction_dict[direction]  
        name2 = "embed_aggre_word_" + direction + "_pure"

        embed_word_align = tf.nn.tanh(
            tf.matmul(embed_word, W_a) + b_a, name=name1)  # 1 * dim
        attention = tf.nn.softmax(
            tf.matmul(embed_opposite_candidates, \
            tf.transpose(embed_word_align)), axis=0)
        
        embed_candidates = attention * embed_opposite_candidates
        
        attention = tf.reduce_sum(
            embed_candidates, axis=0, keepdims=True, name=name2)
                                  
        return attention

    def call(self, embed_word_l, embed_word_r, 
            embed_candidates_l, embed_candidates_r):
        
        embed_aggre_word_l = Attention.determine_attention("l", embed_word_l, 
            embed_candidates_r, self.W_a, self.b_a)

        embed_aggre_word_r = Attention.determine_attention("r", embed_word_r, 
            embed_candidates_l, self.W_a, self.b_a)
        
        return embed_aggre_word_l, embed_aggre_word_r


class PhraseVec(tf.keras.layers.Layer):
    """It concatenates candidate and word embeddings after attention values
       are calculated."""

    def __init__(self, params):
        super(PhraseVec, self).__init__()
        
        self.W_c = tf.Variable(tf.random.truncated_normal(
            [2 * params[0], params[0]], stddev=1.0), tf.float32, name='W_c')
        self.b_c = tf.Variable(
            tf.zeros([1, params[0]]), tf.float32, name='b_c')
        

    def call(
            self, embed_word_r, embed_word_l, embed_aggre_word_r_pure, 
            embed_aggre_word_l_pure):

        embed_words_whole = embed_word_r + embed_word_l
        
        embed_candidates_whole = embed_aggre_word_r_pure \
                                 + embed_aggre_word_l_pure
        
        phrase_vec = tf.math.tanh(
            tf.matmul(
            tf.concat([embed_words_whole, embed_candidates_whole], 1), \
                       self.W_c) + self.b_c, name="phrase_vec")
        
        return phrase_vec


class Output(tf.keras.layers.Layer):
    """Logits layer with raw predictions for the classes."""
    
    def __init__(self, candidate_embeds, name=None):
        super(Output, self).__init__()
        self.candidate_embeds = candidate_embeds

    def call(self, phrase_vec):
        output = tf.matmul(phrase_vec, tf.transpose(self.candidate_embeds))
        
        return output


class Nilinker(tf.keras.Model):
    """Instantiates the NILINKER model integrating all the layers
       as well methods for training, evaluation, and prediction."""

    def __init__(self, word_embeds, candidate_embeds, 
            params, wc, kb_id_to_name, embeds_words2id):
        
        super(Nilinker, self).__init__()
        self.word_embeds = tf.Variable(
                                tf.constant(
                                    word_embeds, shape=[word_embeds.shape[0], 
                                    word_embeds.shape[1]], dtype=tf.float32), 
                                    trainable=False, 
                                    name='word_embeds')
        self.candidate_embeds = tf.Variable(
                                    tf.constant(
                                        candidate_embeds, 
                                        shape=[params[1], params[0]], 
                                        dtype=tf.float32), 
                                        trainable=True, 
                                        name='candidate_embeds')
        self.first_layer = Words2embed(
                                wc, self.word_embeds, self.candidate_embeds)#, 
                                #kb_id_to_name)
        self.attention_layer = Attention(params)
        self.phrase_layer = PhraseVec(params)
        self.output_layer = Output(self.candidate_embeds)
        self.optimizer = None
        self.candidate_num = wc.candidate_num
        self.id2candidate = wc.id2candidate
        self.wc_word2id = wc.word2id
        self.embeds_word2id = embeds_words2id
        self.id_to_name = kb_id_to_name
        self.top_k= params[2]

    def call(self, input):
       
        top_candidates_list = list()
        y_pred_list = list()
        
        for entity in input:
            embed_word_l, embed_word_r, \
                embed_candidates_l, embed_candidates_r = self.first_layer(
                                                           entity)  

            # 2nd layer: attention
            embed_aggre_word_l, embed_aggre_word_r = self.attention_layer(
                                                        embed_word_l, 
                                                        embed_word_r,
                                                        embed_candidates_l, 
                                                        embed_candidates_r)
            
            # 3rd layer: concatenation of word + candidate embeddings
            phrase_vec = self.phrase_layer(
                embed_word_r, embed_word_l, embed_aggre_word_r, 
                embed_aggre_word_l)
            
            # 4th layer: logits output layer
            output = self.output_layer(phrase_vec)
            
            # 5th layer: Activation (final layer)
            y_pred_ent = tf.nn.softmax(output)
            y_pred_list.append(y_pred_ent)

            
            candidates_rank = tf.nn.top_k(
                y_pred_ent, k=self.candidate_num)#sorted=True)
            
            ent_candidates = list()

            for i in range(0, self.top_k):
                cand = int(candidates_rank[1][0][i])
                ent_candidates.append(cand)

            top_candidates_list.append(ent_candidates)
        
        y_pred_tensor = tf.reshape(
            y_pred_list, [len(input), self.candidate_num])
        
        return y_pred_tensor, top_candidates_list

    def predict_step(self, input):
        
        # Input is a batch, even if it only contains 1 entity:
        # To ensure compatibility with train and test modes
        y_pred, top_candidates = self(input)
        
        top_candidates_kb_ids = [
            self.id2candidate[candidate] for candidate in top_candidates[0]]
        top_candidates_names = [
            self.id_to_name[kb_id] for kb_id in top_candidates_kb_ids if kb_id in self.id_to_name.keys()]
  
        output = [(top_candidates_kb_ids[i], top_candidates_names[i]) 
            for i in range(len(top_candidates_names))]
        
        output = tf.expand_dims(output, axis=0)
        
        return output
    
    def prediction(self, entity_str):
        """Wrapper function to preprocess the given entity and to input it to
        the NILINKER model. It returns the top k KB candidates (names and KB
        ids).  
        """
        
        # The first stept is the pre-processing of the inputed entity.
        # The string has to be converted into the following format:
        # 
        #              [wc_word_l_id, wc_word_r_id,
        #               embeds_word_l_id, embeds_word_r_id,
        #               gold_label_id]

        wc_word_l_id, wc_word_r_id = get_words_ids_4_entity(
                                    entity_str, 
                                    wc_word2id=self.wc_word2id,
                                    mode='wc')
        
        embeds_word_l_id, \
           embeds_word_r_id = get_words_ids_4_entity(
                                   entity_str, 
                                   embeds_word2id=self.embeds_word2id,
                                   mode='embeds')
                               
        input_entity = (wc_word_l_id, wc_word_r_id,
                        embeds_word_l_id, embeds_word_r_id)
        
        # Now apply NILINKER to predict relevant KB concepts  
        top_candidates = self.predict([input_entity])
        
        output = list()
        
        for tmp in top_candidates:
            
            for cand in tmp:
                kb_id = cand[0].decode('utf-8')
                cand_name = cand[1].decode('utf-8')
                output.append((kb_id, cand_name))
   
        return output