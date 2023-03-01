

BENT: Biomedical Entity Annotator
---------------------------------

Python Library for Named Entity Recognition (NER) and Linking (NEL) in the biomedical domain.

BENT can be used for: 

* Named Entity Recogniton (NER)
* Named Entity Linking (NEL) 
* Named Entity Recognition and Linking (NER+NEL)

Access the full `documentation <https://bent.readthedocs.io/en/latest/>`__.

Citation::

  Pedro Ruas and Francisco M. Couto. `Nilinker: attention-based approach to nil entity linking. 
  Journal of Biomedical Informatics, 132:104137, 2022. 
  doi: https://doi.org/10.1016/j.jbi.2022.104137.

Installation
~~~~~~~~~~~~~~~~~~~

To use the current version of BENT it is required: 

* OS based on Ubuntu/Debian 
* Conda environment (using `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__ or `Anaconda <https://docs.conda.io/en/latest/>`__ )
* Python>=3.7
* Required space between 5.5 GB - 10 GB 
   * Dependencies: 2.5 GB 
   * Data: between 3.0 GB (base) or 7.5 GB (if you use all available knowlegde bases for NEL)


.. note::

   Please ensure that you have the appropriate version of Conda installed.


Create a Conda environment (adapt for the name of your project):

::

   conda create --name annotation_project python=3.7


Activate the environment:

::

   conda activate annotation_project


Install the BENT package using pip:

::

   pip install bent


After the pip installation, it is required a further step to install non-Python dependencies and to download the necessary data. Specify the knowledge bases that will be used:

::

   python -c "from bent.setup_package import setup_package;setup_package([<kb1>, <kb2>, <kb3>])"


Available knowledge bases:

* ‘medic’ (`MEDIC <http://ctdbase.org/>`__)

* ‘do’ (`Disease ontology <https://disease-ontology.org/>`__)

* 'chebi’ (`ChEBI ontology <https://www.ebi.ac.uk/chebi/>`__) 

* ‘ctd_chem’ (`CTD-Chemicals <http://ctdbase.org/>`__)

* ‘ncbi_gene’ (`NCBI Gene <https://www.ncbi.nlm.nih.gov/gene/>`__)

* ‘ctd_gene’ (`CTD-GENES <http://ctdbase.org/>`__)

* ‘ncbi_taxon’ (`NCBI Taxonomy <https://www.ncbi.nlm.nih.gov/taxonomy>`__)

* ‘go_bp’ (`Gene Ontology-Biological Process <http://geneontology.org/>`__)

* ‘ctd_anat’ (`CTD-Anatomy <http://ctdbase.org/>`__)

* ‘uberon’ (`UBERON ontology <http://obophenotype.github.io/uberon/>`__)

* ‘go_cc’ (`Gene Ontology-Cellular Component <http://geneontology.org/>`__)

* ‘cell_ontology’ (`Cell Ontology <https://cell-ontology.github.io/>`__)

* cellosaurus’ (`Cellosaurus <https://www.cellosaurus.org/>`__)


Example to download **only** the MEDIC vocabulary:

::

   python -c "from bent.setup_package import setup_package;setup_package(['medic'])"


If you want to download **all** knowledge bases, choose the option 'all':

::

   python -c "from bent.setup_package import setup_package;setup_package(['all'])"


You can download more knowledge bases later by:
   
   * specifying the desired knolwedge bases 
   * setting the argument 'only_kb_dicts' to True
   * running the same command with these changes:


Example:

::

   python -c "from bent.setup_package import setup_package;setup_package(['chebi'], only_kb_dicts=True)"


Reinitiate the conda environment.


Get started
~~~~~~~~~~~

To apply the complete pipeline of entity extraction (NER+NEL) set the arguments:

* **recognize**: indicate that the NER module will be applied ('True')
* **link**: indicate that the NEL module will be applied ('True')
* **types**: entity types to recognize and the respective target knowledge bases.
* **in_dir**: directory path containing the text files to be annotated (the directory must contain text files exclusively)
* **out_dir**: the output directory that will contain the annotation files


Example:

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


It is also possible to apply the pipeline (NER+NEL) to a string or a list or strings instantiated in the execution script.

To see more usage examples, access the `documentation <https://bent.readthedocs.io/en/latest/usage.html>`__.
