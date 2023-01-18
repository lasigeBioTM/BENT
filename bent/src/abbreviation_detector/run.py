#!/usr/bin/env python

import bent.src.cfg as cfg
import os


def parse_Ab3P_output(filepaths, initial_dir):
    """Parse the output of the Ab3P tool from a text file into a dictionary
    for later reuse.

    :param filepaths: paths of the files that were outputted by Ab3P
    :type filepaths: list
    :return: abbreviations with format: {'doc_id': {'abbv1': 'long_form'}]
    :rtype: dict
    """

    abbreviations = {}
    doc_id = ''
    
    for filepath in filepaths:
        doc_abbrvs = {}
       
        if '.txt' in filepath or '.ann' in filepath:
            doc_id = filepath[:-4]
        
        else:
            doc_id = filepath

        filepath_up = 'tmp/{}_abbrvs'.format(doc_id)
        
        with open(filepath_up, 'r') as out_file:
            data = out_file.readlines()
            out_file.close()
            
            for line in data:

                if line[0] == ' ': 
                    line_data = line.split('|')
                    
                    if len(line_data) == 3:
                        score = float(line_data[2])

                        if score >= 0.90:
                            doc_abbrvs[line_data[0].strip(' ')] = line_data[1]

        # Remove the generated txt files
        comm1 = 'rm {}'.format(filepath_up)
        os.system(comm1)
        
        abbreviations[doc_id] = doc_abbrvs
    
    # Return to the original dir
    os.chdir(initial_dir)

    return abbreviations


def run_Ab3P(input_dir):
    """Apply the abbreviation detector Ab3P in the texts located in input_dir. 

    :param input_dir: path to the directory including the texts of the 
        documents where the entities were recognized
    :type input_dir: str
    :return: abbreviations with format: {'doc_id': {'abbv1': 'long_form'}]
    :rtype: dict
    """

    filepaths = [file for file in os.listdir(input_dir)]

    # change to Ab3P directory
    cwd = os.getcwd()
    os.chdir(cfg.root_path + 'scripts/abbreviation_detector/Ab3P/')

    if not os.path.exists('tmp/'):
        os.mkdir('tmp/')

    # Run Ab3P for each text file
    for filepath in filepaths:
        doc_id = ''

        if '.txt' in filepath or '.ann' in filepath:
            doc_id = filepath[:-4]
        
        else:
            doc_id = filepath

        comm = './identify_abbr ../../../{}{} 2> /dev/null >> tmp/{}_abbrvs'.format(
            input_dir, filepath, doc_id)
        os.system(comm)
    
    # Return to the original dir
    #os.chdir('../../../')

    return parse_Ab3P_output(filepaths, cwd) 