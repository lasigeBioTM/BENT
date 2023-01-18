#!/usr/bin/env python
"""This module parses biomedical knowledge bases into several types of 
objects (dictionaries and Networkx graph)."""

import csv
import networkx as nx
import obonet
import bent.src.cfg as cfg

data_dir = cfg.root_path + 'data/kbs/original_files/'


class KnowledgeBase:
    """Represents a knowledge base that is loaded from a given local file."""

    def __init__(self, kb, mode, terms_filename=None, edges_filename=None, 
            kb_filename=None, input_format=None):
        
        self.kb = kb
        self.mode = mode # reel or nilinker 
        self.terms_filename = terms_filename
        self.edges_filename = edges_filename
        self.kb_filename = kb_filename
        self.input_format = input_format # obo, tsv, csv, txt

        if mode == 'reel':
            self.root_dict = {"go_bp": ("GO_0008150", "biological_process"), 
                            "go_cc": ("GO_0005575", "cellular_component"), 
                            "chebi": ("CHEBI_00", "root"), 
                            "hp": ("HP_0000001", "All"), 
                            "medic": ("MESH_C", "Diseases"), 
                            "ctd_anat": ("MESH_A", "Anatomy"), 
                            "ctd_chem": ("MESH_D", "Chemicals"),
                            "ctd_gene": ("", ""), 
                            "do": "DOID_4"}
        
        elif mode == 'nilinker':
            self.root_dict = {"go_bp": ("GO:0008150", "biological_process"), 
                            "chebi": ("CHEBI:00", "root"), 
                            "hp": ("HP:0000001", "All"), 
                            "medic": ("MESH:C", "Diseases"), 
                            "ctd_anat": ("MESH:A", "Anatomy"), 
                            "ctd_chem": ("MESH:D", "Chemicals")}
        
        obo_file = {'chebi', 'hp', 'medic', 'do', 'go_bp', 'go_cc', 
            'cellosaurus', 'cl', 'uberon'}
        self.tsv_file = {'ctd_chem', 'ctd_anat', 'ctd_gene'}
        self.csv_file = {'ncbi_taxon'}
        self.other = {'ncbi_gene'}
        self.name_to_id = None
        self.id_to_info = None
        self.synonym_to_id = None
        self.graph = None
        self.child_to_parent = None
        self.alt_id_to_id = None
        self.umls_to_hp = None

        #---------------------------------------------------------------------
        #                 Load the info about the given KB
        #---------------------------------------------------------------------
        if kb == 'chebi' and mode == 'nilinker':
            loaded_kb = KnowledgeBase.load_partial_chebi(self)
                
        else:

            if kb in obo_file or input_format == 'obo':
                self.load_obo()
                
            elif self.kb in self.tsv_file or self.input_format == 'tsv':
                self.load_tsv()
                    
            elif self.kb == 'ncbi_taxon':
                self.load_ncbi_taxon()
            #elif self.kb in self.csv_file or self.input_format == 'csv':
            #    self.load_csv()
            
            elif self.kb == 'ncbi_gene':
                self.load_ncbi_gene()
            
            else:
                 
                if self.input_format == 'txt':
                    self.load_txt()
    
    def load_obo(self):
        """Load KBs from local .obo files (ChEBI, HP, MEDIC, GO) into 
        structured dicts containing the mappings name_to_id, id_to_name, 
        id_to_info, synonym_to_id, child_to_parent, umls_to_hp and the list of 
        edges between concepts. For 'chebi', only the concepts in the subset 
        3_STAR are included, which correpond to manually validated entries. 
        
        :param kb: target ontology to load, has value 'medic', 'chebi', 
            'go_bp' or 'hp'
        :type kb: str
        """
        
        filepath =  data_dir
        filepaths = {'medic': 'CTD_diseases', 'chebi': 'chebi', 
                        'go_bp': 'go-basic', 'go_cc': 'go-basic', 
                        'do': 'doid', 'hp': 'hp',
                        'cellosaurus': 'cellosaurus', 'cl': 'cl-basic',
                        'uberon': 'uberon-basic'
                        }

        if self.kb in filepaths.keys():
            filepath += filepaths[self.kb] + '.obo' 
       
        else:
            filepath += + self.kb_filename
        
        name_to_id = {}
        id_to_name = {}
        id_to_info = {}
        synonym_to_id = {}
        child_to_parent = {}
        alt_id_to_id = {}
        umls_to_hp = {}

        graph = obonet.read_obo(filepath)
        edges = []
        
        for node in  graph.nodes(data=True):
            add_node = False
            
            if "name" in node[1].keys():
                node_id, node_name = node[0], node[1]["name"]

                if self.mode == 'reel':
                    node_id = node_id.replace(':', '_')
                
                if self.kb == "go_bp": 
                    # For go_bp, ensure that only Biological Process 
                    # concepts are considered
                    
                    if node[1]['namespace'] == 'biological_process':
                        name_to_id[node_name] = node_id
                        id_to_name[node_id] = node_name
                        #id_to_info[node_id] = node_name
                        add_node = True
                
                elif self.kb == 'go_cc':

                    if node[1]['namespace'] == 'cellular_component':
                        name_to_id[node_name] = node_id
                        id_to_name[node_id] = node_name
                        #id_to_info[node_id] = node_name
                        add_node = True

                elif self.kb == "medic":

                    #if node_id[0:4] != "OMIM": 
                    #    # Exclude OMIM concepts #TODO: revise later
                    name_to_id[node_name] = node_id
                    id_to_name[node_id] = node_name
                    add_node = True
                    
                else:
                    name_to_id[node_name] = node_id
                    id_to_name[node_id] = node_name
                    add_node = True

                if 'alt_id' in node[1].keys():
                
                    for alt_id in node[1]['alt_id']:
                        alt_id_to_id[alt_id.replace(':', '_')] = node_id

                if 'is_obsolete' in node[1].keys() and \
                        node[1]['is_obsolete'] == True:
                    add_node = False
                    del name_to_id[node_name]
                    del id_to_name[node_id]
                
                # Check parents for this node
                if 'is_a' in node[1].keys() and add_node: 
                    # The root node of the ontology does not 
                    # have is_a relationships

                    if len(node[1]['is_a']) == 1: 
                        # Only consider concepts with 1 direct ancestor
                        child_to_parent[node_id] = node[1]['is_a'][0]

                    for parent in node[1]['is_a']: 
                        # To build the edges list, consider all 
                        # concepts with at least one ancestor
                        #edges.append((node_id,parent))         
                        edges.append((parent.replace(':', '_'), node_id))

                if self.kb == 'cellosaurus':
                    
                    if 'relationship' in node[1].keys() and add_node:
                        relations = node[1]['relationship']
                        
                        for relation in relations:
                            
                            if relation[:13] == 'derived_from ':
                                parent = relation.split('derived_from')[1][1:]
                                edges.append((parent, node_id))
                
                if "synonym" in node[1].keys() and add_node: 
                    # Check for synonyms for node (if they exist)
                        
                    for synonym in node[1]["synonym"]:
                        synonym_name = synonym.split("\"")[1]
                        synonym_to_id[synonym_name] = node_id

                if "xref" in node[1].keys() and add_node:

                    if self.kb == "hp": 
                        # Map UMLS concepts to HPO concepts
                        for xref in node[1]['xref']:
                            if xref[:4] == "UMLS":
                                umls_id = xref.strip("UMLS:")
                                umls_to_hp[umls_id] =  node_id 
        
        if self.kb in self.root_dict.keys():
            root_concept_name = self.root_dict[self.kb][1]
            root_id = str()
        
            if root_concept_name not in name_to_id.keys():
                root_id = self.root_dict[self.kb][0]
                name_to_id[root_concept_name] = root_id
                id_to_name[root_id] = root_concept_name
        
        #----------------------------------------------------------------------
        # Add misssing edges between the ontology root and 
        # sub-ontology root concepts
        if self.kb == 'chebi':
            chemical_entity = "CHEBI_24431"
            edges.append((chemical_entity, root_id))
            role = "CHEBI_50906"
            edges.append((role, root_id))
            subatomic_particle = "CHEBI_36342"
            edges.append((subatomic_particle, root_id))
            application = "CHEBI_33232"
            edges.append((application, root_id))
        
        kb_graph = nx.DiGraph([edge for edge in edges])
        
        # Build id_to_info (KB-ID: (outdegree, indegree, num_descendants))
        for node in kb_graph.nodes:
            num_descendants = len(nx.descendants(kb_graph, node))

            id_to_info[node] = (
                kb_graph.out_degree(node), kb_graph.in_degree(node), 
                num_descendants)

        node_to_node = {}

        for edge in edges:
            
            if edge[0] in node_to_node:
                node_to_node[edge[0]].append(edge[1])
            
            else:
                node_to_node[edge[0]] = [edge[1]]

            if edge[1] in node_to_node:
                node_to_node[edge[1]].append(edge[0])
            
            else:
                node_to_node[edge[1]] = [edge[0]]
        
        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.id_to_info = id_to_info
        self.synonym_to_id = synonym_to_id
        self.graph = kb_graph
        self.child_to_parent = child_to_parent
        self.alt_id_to_id = alt_id_to_id
        self.umls_to_hp = umls_to_hp
        self.node_to_node = node_to_node
            
    def load_tsv(self):
        """Load KBs from local .tsv files (CTD-Chemicals, CTD-Anatomy) 
           into structured dicts containing the mappings name_to_id, 
           id_to_info, synonym_to_id, child_to_parent, and the list of edges 
           between concepts.
        
        :param kb: target ontology to load, has value 'ctd_chem' or 'ctd_anat'
        :type kb: str
        """
                
        kb_dict = {"ctd_chem": "CTD_chemicals", "ctd_anat": "CTD_anatomy",
            "ctd_gene": "CTD_genes"}
        filepath = data_dir + kb_dict[self.kb] + ".tsv"
        
        name_to_id = {}
        id_to_name = {}
        id_to_info = {}
        synonym_to_id = {}
        child_to_parent= {}
        edges = []

        with open(filepath) as kb_file:
            reader = csv.reader(kb_file, delimiter="\t")
            row_count = int()
        
            for row in reader:
                row_count += 1
                
                if row_count >= 30:
                    node_name = row[0] 
                    node_id = row[1]
                    
                    if self.mode == 'reel':
                        node_id = node_id.replace(':', '_')
                    
                    node_parents = row[4].split('|')
                    synonyms = row[7].split('|')
                    name_to_id[node_name] = node_id
                    id_to_name[node_id] = node_name
              
                    if len(node_parents) == 1: #
                        # Only consider concepts with 1 direct ancestor
                        child_to_parent[node_id] = node_parents[0]
                    
                    for synonym in synonyms:
                        synonym_to_id[synonym] = node_id

                    for parent in node_parents: 
                        # To build the edges list, consider 
                        # all concepts with at least one ancestor
                        edges.append((parent.replace(':', '_'), node_id ))
        
        root_concept_name = self.root_dict[self.kb][1]
        root_concept_id = self.root_dict[self.kb][0]
        name_to_id[root_concept_name] = root_concept_id
        id_to_name[root_concept_id] = root_concept_name

        kb_graph = nx.DiGraph([edge for edge in edges])

        # Build id_to_info (KB-ID: (outdegree, indegree, num_descendants))
        for node in kb_graph.nodes:
            num_descendants = len(nx.descendants(kb_graph, node))

            id_to_info[node] = (
                kb_graph.out_degree(node), kb_graph.in_degree(node), 
                num_descendants)

        node_to_node = {}

        for edge in edges:
            
            if edge[0] in node_to_node:
                node_to_node[edge[0]].append(edge[1])
            
            else:
                node_to_node[edge[0]] = [edge[1]]

            if edge[1] in node_to_node:
                node_to_node[edge[1]].append(edge[0])
            
            else:
                node_to_node[edge[1]] = [edge[0]]
    
        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.id_to_info = id_to_info
        self.synonym_to_id = synonym_to_id
        self.graph = kb_graph
        self.child_to_parent = child_to_parent
        self.node_to_node = node_to_node
    
    def load_ncbi_taxon(self):
        """Load KBs from local .csv files (NCBITaxon) into structured dicts 
            containing the mappings name_to_id, id_to_info, synonym_to_id.
        
        :param kb: target ontology to load, has value 'ncbi_taxon'
        :type kb: str
        """

        filepath = data_dir
        
        if self.kb == 'ncbi_taxon':
            filepath += 'NCBITAXON.csv'
        
        name_to_id = {}
        id_to_name = {}
        id_to_info = {}
        synonym_to_id = {}
        child_to_parent = {}       
        edges = []

        with open(filepath) as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            row_count = int()
            
            for row in reader:
                row_count += 1

                if row_count > 1 and 'NCBITAXON/' in row[0]:
                    rank_node = row[9]

                    if rank_node == 'species':
                        node_name = row[1] 
                        node_id =  'NCBITaxon_' + row[0].split('NCBITAXON/')[1]
                        synonyms = row[2].split('|')
                        name_to_id[node_name] = node_id
                        id_to_name[node_id] = node_name
                        
                        if row[7] != '':
                            parent_id = 'NCBITaxon_' + row[7].split('NCBITAXON/')[1]
                            relationship = (node_id, parent_id)
                            edges.append(relationship)

                            #if len(node_parents) == 1: #
                            # Only consider concepts with 1 direct ancestor
                            child_to_parent[node_id] = parent_id
                        
                        for synonym in synonyms:
                            synonym_to_id[synonym] = node_id

        # Create a MultiDiGraph object with only "is-a" relations 
        # this will allow the further calculation of shorthest path lenght
        kb_graph = nx.DiGraph([edge for edge in edges])

        # Build id_to_info (KB-ID: (outdegree, indegree, num_descendants))
        for node in kb_graph.nodes:
            num_descendants = len(nx.descendants(kb_graph, node))

            id_to_info[node] = (
                kb_graph.out_degree(node), kb_graph.in_degree(node), 
                num_descendants)

        node_to_node = {}
        
        for edge in edges:
            
            if edge[0] in node_to_node:
                node_to_node[edge[0]].append(edge[1])
            
            else:
                node_to_node[edge[0]] = [edge[1]]

            if edge[1] in node_to_node:
                node_to_node[edge[1]].append(edge[0])
            
            else:
                node_to_node[edge[1]] = [edge[0]]

        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.id_to_info = id_to_info
        self.synonym_to_id = synonym_to_id
        self.graph = kb_graph
        self.node_to_node = node_to_node

    def load_ncbi_gene(self):

        name_to_id = {}
        id_to_name = {}
        id_to_info = {}
        synonym_to_id = {}
        
        with open(data_dir + "All_Data.gene_info") as ncbi_gene:
            reader = csv.reader(ncbi_gene, delimiter="\t")
            row_count = int()
            
            for row in reader:
                row_count += 1
                
                if row_count > 7:
                    #Skip the header
                    gene_symbol = row[2]
                    gene_id = 'NCBIGene_' +row[1]
                    synonyms = row[4].split('/')
                    description = row[8]
                    synonym_to_id[description] = gene_id
                    
                    name_to_id[gene_symbol] = gene_id
                    id_to_name[gene_id] = gene_symbol
                    
                    for synonym in synonyms:

                        if synonym != '-':
                            synonym_to_id[synonym] = gene_id

        edges = [('NCBIGene1', 'NCBIGene2')]
        kb_graph = nx.DiGraph([edge for edge in edges])

        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.id_to_info = id_to_info
        self.synonym_to_id = synonym_to_id
        self.graph = kb_graph
        self.node_to_node = {}
        
    def load_txt(self):

        name_to_id = {}
        id_to_name = {}
        id_to_info = {}
        synonym_to_id = {}
        edges = []

        # import concept names
        with open(self.terms_filename, 'r') as in_file:
            data = in_file.readlines()

            for line in data:
                
                if line != '\n':
                    line_ = line.strip('\n').split(' ')
                    kb_id = line_[0]
                    name = line_[1]
                    name_to_id[name] = kb_id
                    id_to_name[kb_id] = name

                    if len(line_) == 3:
                        synonyms = line_[2].split(';')
                        
                        for synonym in synonyms:
                            synonym_to_id[synonym] = kb_id

        # import relations between concepts
        edges = []

        with open(self.edges_filename, 'r') as in_file:
            data = in_file.readlines()

            for line in data:
                
                if line != '\n':
                    line_ = line.strip('\n').split(' ') # Change for \t
                    term1 = line_[0]
                    term2 = line_[1]
                    edges.append((term1, term2))

        kb_graph = nx.DiGraph([edge for edge in edges])

        # Build id_to_info (KB-ID: (outdegree, indegree, num_descendants))
        for node in kb_graph.nodes:
            num_descendants = len(nx.descendants(kb_graph, node))

            id_to_info[node] = (
                kb_graph.out_degree(node), kb_graph.in_degree(node), 
                num_descendants)

        node_to_node = {}
        
        for edge in edges:
            
            if edge[0] in node_to_node:
                node_to_node[edge[0]].append(edge[1])
            
            else:
                node_to_node[edge[0]] = [edge[1]]

            if edge[1] in node_to_node:
                node_to_node[edge[1]].append(edge[0])
            
            else:
                node_to_node[edge[1]] = [edge[0]]

        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.id_to_info = id_to_info
        self.synonym_to_id = synonym_to_id
        self.node_to_node = node_to_node
        self.graph = kb_graph

    def load_partial_chebi(self):
        """Load ChEBI ontology, but only the manually validated concepts 
        (3-start). It is only used when applying the NILINKER model."""

        assert self.mode == 'nilinker', 'Partial ChEBI is being loaded!'

        kb_dir = data_dir

        name_to_id = {}
        id_to_name = {}
        synonym_to_id = {}
        child_to_parent = {}
        ancestors_count = {}

        edges = [] 
        terms_to_include = [],

        # Import relations between ChEBI concepts
        with open(kb_dir + 'relation_3star.tsv') as relations_file:
            reader = csv.reader(relations_file, delimiter='\t')
            
            for row in reader:
                
                if row[1] == 'is_a':
                    term1 = 'CHEBI:' + row[2]
                    term2 = 'CHEBI:' + row[3]
                    
                    edges.append((term1, term2))
    
                    if term1 not in terms_to_include:
                        terms_to_include.append(term1)

                    if term2 not in terms_to_include:
                        terms_to_include.append(term2)

                    if term1 in ancestors_count.keys():
                        added = ancestors_count[term1]
                        added += 1
                        ancestors_count[term1] = added
                    
                    else:
                        ancestors_count[term1] = 1

            relations_file.close()
        
        # Import concept names
        with open(kb_dir + 'compounds_3star.tsv') as names_file:
            reader = csv.reader(names_file, delimiter='\t')

            for row in reader:
                
                chebi_id = row[2]
                name = row[5]

                if chebi_id in terms_to_include and name != 'null':
                    name_to_id[name] = chebi_id
                    id_to_name[chebi_id] = name

            names_file.close()

        # Import synonyms
        with open(kb_dir + 'names_3star.tsv') as syn_file:
            reader = csv.reader(syn_file, delimiter='\t')

            for row in reader:
                chebi_id = 'CHEBI:' + row[1]
                syn_name = row[4]

                if chebi_id in terms_to_include:
                    synonym_to_id[syn_name] = chebi_id
                    
            syn_file.close()
    
        # Add edges between the ontology root and sub-ontology root concepts
        root_concept_name = self.root_dict['chebi'][1]
        root_id = self.root_dict['chebi'][0]
        name_to_id[root_concept_name] = root_id
        id_to_name[root_id] = root_concept_name
        
        chemical_entity = "CHEBI:24431"
        edges.append((chemical_entity, root_id))
        role = "CHEBI:50906"
        edges.append((role, root_id))
        subatomic_particle = "CHEBI:36342"
        edges.append((subatomic_particle, root_id))
        application = "CHEBI:33232"
        edges.append((application, root_id))

        # Find child-parent links
        for edge in edges:
            child = edge[0]
            parent = edge[1]

            if child in ancestors_count.keys() and ancestors_count[child] == 1:
                # The term has only 1 direct ancestor
                child_to_parent[child] = parent

        self.name_to_id = name_to_id
        self.id_to_name = id_to_name
        self.synonym_to_id = synonym_to_id
        self.child_to_parent = child_to_parent