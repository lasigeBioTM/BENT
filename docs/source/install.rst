Installation
============

To use the current version of BENT it is required: 

|:arrow_right:| Ubuntu/Debian based OS

|:arrow_right:| `Conda <https://docs.conda.io/en/latest/>`__ environment 

|:arrow_right:| Python>=3.7

|:arrow_right:| Between 11 and 15 GB (5 GB Anaconda + 2.5 GB to install dependencies + 3.0 GB data or 7.5 GB if you use all available knowlegde bases for NEL)


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

Example to download only the MEDIC vocabulary:

::

   python -c "from bent.setup_package import setup_package;setup_package(['medic'])"


If you want to download all knowledge bases, choose the option 'all':

::

   python -c "from bent.setup_package import setup_package;setup_package(['all'])"


You can download more knowledge bases later by running the same command and specifying the desired knolwedge bases among the ones that are available and setting the argument ' only_kb_dicts' to True:

::

   python -c "from bent.setup_package import setup_package;setup_package([<kb>],  only_kb_dicts=True)"


Reinitiate the conda environment.
