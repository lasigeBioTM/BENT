Usage
=======

BENT can be used for: 

|:arrow_right:| Named Entity Recognition (NER) 

|:arrow_right:| Named Entity Linking (NEL) 

|:arrow_right:| Named Entity Recognition and Linking (NER+NEL)

Contents 
---------

- `Usage <#usage>`__ 
   - `Named Entity Recogniton (NER) <#named-entity-recogniton-ner>`__ 
      - `Text files as input <#text-files-as-input>`__ 
      - `List of texts as input <#list-of-texts-as-input>`__ 
      - `Single text as input <#single-text-as-input>`__ 
   - `Named Entity Linking (NEL) <#named-entity-linking-nel>`__ 
      - `Link entities in annotation files <#link-entities-in-annotation-files>`__ 
   - `Named Entity Recognition and Linking (NER+NEL) <#named-entity-recognition-and-linking-nernel>`__ 
   - `Upload custom knowledge base/graph/ontology <#upload-custom-knowledge-basegraphontology>`__


Named Entity Recogniton (NER)
-----------------------------

BENT includes 10 NER models. Each model corresponds to `PubMedBERT <https://huggingface.co/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext>`__ fine-tuned on specific datasets.

The models and the description of the training datasets are stored in `Hugging Face <https://huggingface.co/>`__. The available models are:

* ‘disease’: disease entities.

* ‘chemical’: chemical entities.

* ‘gene’: gene and protein entities.

* ‘organism’: organism (species, genus, …) entities.

* ‘bioprocess’: biological process entities (as defined by Gene Ontology-Biological Process sub-ontology)

* ‘anatomical’: anatomical entities

* ‘cell_component’: cell component entities

* ‘cell_type’: cell type entities

* ‘cell_line’: cell line entities

* ‘variant’: variant entities (a DNA-level or protein-level mutation as defined by the `Human Genome Variation Society nomenclature <http://varnomen.hgvs.org/>`__).

.. note::
   In the current version, the ouput of both NER and NEL is only available for the `BRAT standoff format <https://brat.nlplab.org/standoff.html>`__.


Text files as input
~~~~~~~~~~~~~~~~~~~

To recognize disease entities in text files placed under the directory ‘input/’ set the argument ‘types’:

::

   import bent.annotate as bt

   bt.annotate(
           recognize=True,
           types={'disease': ''},
           in_dir='input/txt/',
           out_dir='output/ner/'
   )

The annotations files (‘.ann’) will be under the directory ‘output/ner/’.

.. note::
   Ensure that the only files in the ‘input_dir/txt/’ are the text files that you want to annotate.


List of texts as input
~~~~~~~~~~~~~~~~~~~~~~

To recognize disease, chemical, gene, anatomical, cell line and bioprocess entities in texts provided in an input list:

::

   import bent.annotate as bt

   # Each element of the list corresponds to a different document text
   txt_list = [
       'Caffeine is a central nervous system (CNS) stimulant. It is hypothesized that caffeine innhibits the activation NF-kappaB in A2058 melanoma cells.', 
       'The Parkinson disease is a degenerative disorder affecting the motor system. PARK2 gene expression is associated with the Parkinson disease.']

   bt.annotate(
           recognize=True,
           types={
               'disease': '',
               'chemical': '',
               'gene': '',
               'anatomical': '',
               'cell_line': '',
               'bioprocess': ''
                  },
           input_text=txt_list,
           out_dir='output/ner/'
   )

For each input text will be generated an annotation files (‘.ann’), placed under the directory ‘output/ner’. 

The output will follow the BRAT format:

doc1.ann:

::

   T1  chemical 0 7    Caffeine
   T2  anatomical 13 35    central nervous system
   T3  anatomical 37 40    CNS
   T4  chemical 77 85  Caffeine
   T5  gene 111 120    NF-kappaB
   T1  chemical 0 8    Caffeine
   T6  cell_line 124 129 A2058


doc2.ann:

::

   T1  disease 3 21    Parkinson disease 
   T2  anatomical 63 75    motor system    
   T3  gene 77 82  PARK2   
   T4  bioprocess 83 98    gene expression 
   T5  disease 122 139 Parkinson disease   


Single text as input
~~~~~~~~~~~~~~~~~~~~

To recognize disease entities in a text provided as a string and to output the annotations as a ‘dataset’ object ommiting the ‘out_dir’ argument:

::

   import bent.annotate as bt

   txt1 = 'Reed's Sindrome has several manifestations and symptoms.'

   dataset = bt.annotate(
           recognize=True,
           types={'disease': ''},
           input_text=txt1,
   )


It is possible to access the ‘dataset’ object:

::

   for doc in dataset.documents:
       print(doc.id)

       for entity in doc.entities:
           print(entity.type)
           print(entity.text)


Which will output:

::

   disease 
   Reed's Sindrome     


Named Entity Linking (NEL)
--------------------------

BENT includes pre-process dictionaries that allow the linking of recognized entities of different types to entries of the following knowledge bases/graphs/ontologies:

* ‘disease’ |:arrow_right:| ‘medic’ (`MEDIC <http://ctdbase.org/>`__), ‘do’ (`Disease ontology <https://disease-ontology.org/>`__)

* ‘chemical’ |:arrow_right:| ‘chebi’ (`ChEBI ontology <https://www.ebi.ac.uk/chebi/>`__) and ‘ctd_chem’ (`CTD-Chemicals <http://ctdbase.org/>`__)

* ‘gene’ |:arrow_right:| ‘ncbi_gene’ (`NCBI Gene <https://www.ncbi.nlm.nih.gov/gene/>`__), ‘ctd_gene’ (`CTD-GENES <http://ctdbase.org/>`__)

* ‘organism’ |:arrow_right:| ‘ncbi_taxon’ (`NCBI Taxonomy <https://www.ncbi.nlm.nih.gov/taxonomy>`__)

* ‘bioprocess’ |:arrow_right:| ‘go_bp’ (`Gene Ontology-Biological Process <http://geneontology.org/>`__)

* ‘anatomy’ |:arrow_right:| ‘ctd_anat’ (`CTD-Anatomy <http://ctdbase.org/>`__), ‘uberon’ (`UBERON ontology <http://obophenotype.github.io/uberon/>`__)

* ‘cell_component’ |:arrow_right:| ‘go_cc’ (`Gene Ontology-Cellular Component <http://geneontology.org/>`__)

* ‘cell_type’ |:arrow_right:| ‘cell_ontology’ (`Cell Ontology <https://cell-ontology.github.io/>`__)

* ‘cell_line’ |:arrow_right:| ‘cellosaurus’ (`Cellosaurus <https://www.cellosaurus.org/>`__)


Link entities in annotation files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Considering the annotation files outputted before, in this case we also want to link the already recognized entities to entries of several target knowlege bases:

::

   import bent.annotate as bt

   bt.annotate(
           link=True,
           types={
               'disease': 'medic'
               'chemical': 'chebi',
               'gene': 'ncbi_gene',
               'anatomical': 'uberon',
               'cell_line': 'cellosaurus',
               'bioprocess': 'go_bp'
               },
           ner_dir='output/ner/',
           out_dir='output/nel/'
   )


The annotations files (‘.ann’) will be under the directory ‘output/nel/’, but will now include the normalized identifiers for each recognized entity.

.. note::
   In this case, where we already have the annotations files from the NER stage, it is required to set the argument ‘ner_dir’ instead of ‘in_dir’.

The updated output in the BRAT format will be:

doc1.ann:

::

   T1  chemical 0 7    Caffeine
   N1  Reference T1 CHEBI:27732    Caffeine
   T2  anatomical 13 35    central nervous system
   N2  Reference T2 UBERON:0001017 central nervous system
   T3  anatomical 37 40    CNS
   N3  Reference T3 UBERON:0001017 CNS
   T4  chemical 77 85  Caffeine
   N4  Reference T4 CHEBI:27732    Caffeine
   T5  gene 111 120    NF-kappaB
   N5  Reference T5 NCBIGene:4790  NF-kappaB
   T1  chemical 0 8    Caffeine
   N6  Reference T6 CVCL_1059  A2058


doc2.ann:

::

   T1  disease 3 21    Parkinson disease 
   N1  Reference T1 MESH:D010300   Parkinson disease
   T2  anatomical 63 75    motor system    
   N2  Reference T2 UBERON:0025525 motor system
   T3  gene 77 82  PARK2   
   N3  Reference T3 NCBIGene:421577    PARK2
   T4  bioprocess 83 98    gene expression 
   N4  Reference T4 GO:0010467 gene expression
   T5  disease 122 139 Parkinson disease   
   N5  Reference T5 MESH:D010300   Parkinson disease

In the current version, it is not possible yet to provide a dictionary of texts and NER annotations as input to the NEL pipeline.


Named Entity Recognition and Linking (NER+NEL)
-----------------------------------------------

To apply the complete pipeline of entity extraction to a set of files placed in the input directory set the arguments ‘recognize’ and ‘link’ to True:

::

   import bent.annotate as bt

   bt.annotate(
           recognize=True,
           link=True,
           types={
            'disease': 'medic'
            'chemical': 'chebi',
            'gene': 'ncbi_gene',
            'anatomical': 'uberon',
            'cell_line': 'cellosaurus',
            'bioprocess': 'go_bp'
            },
           in_dir='input/txt/',
           out_dir='output/nel/'
   )


Upload custom knowledge base/graph/ontology
--------------------------------------------

If you want to use a custom knowledge base that is not included in the availabe options, it is necessary to have two text files: **terms.txt** and **edges.txt**.

The file **terms.txt** is a list of the entries of the custm knowledge base with the format:

::

   ID:1 Entry 1
   ID:2 Entry 2
   ID:3 entry 3


**edges.txt** is a list of *is-a* (child-parent) relations between the
entries of the **terms.txt** file:

::

   ID:1  ID:3
   ID:2  ID:3

.. note::
   In both files, elements in each line are separated by a tab ('\\t').

Run the following code to generate the files for the custom knowledge
base, indicating the filenames and the desired name:

::

   import  bent.src.setup.kb.generate_dicts  as  bkb

   bkb.generate(
           custom=True,
           kb_name='disease_KG',
           terms_filename='terms.txt',
           edges_filename='edges.txt',
           input_format='txt' 
   )

After this step, you can apply the above pipelines using the newly
generated knowledge base by setting the dictionary 'types':

::

   import bent.annotate as bt

   bt.annotate(
           recognize=True,
           link=True,
           types={'disease': 'disease_KG'},
           in_dir='input/txt/',
           out_dir='output/nel/'
   )
