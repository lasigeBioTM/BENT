Installation
============

To use the current version of BENT it is required: 

*  OS: Ubuntu/Debian 

*  Python 3.7, 3.8 or 3.9

*  Required space between 5.5 GB - 10 GB 
   * Dependencies: 2.5 GB 
   * Data: between 3.0 GB (base) or 7.5 GB (if you use all available knowlegde bases for Named Entity Linking)


Install the BENT package using pip:

::

   pip install bent


The following knowledge bases can be configured:

* 'medic' (`MEDIC <http://ctdbase.org/>`__)

* 'do' (`Disease ontology <https://disease-ontology.org/>`__)

* 'chebi' (`ChEBI ontology <https://www.ebi.ac.uk/chebi/>`__) 

* 'ctd_chem' (`CTD-Chemicals <http://ctdbase.org/>`__)

* 'ncbi_gene' (`NCBI Gene <https://www.ncbi.nlm.nih.gov/gene/>`__)

* 'ctd_gene' (`CTD-GENES <http://ctdbase.org/>`__)

* 'ncbi_taxon' (`NCBI Taxonomy <https://www.ncbi.nlm.nih.gov/taxonomy>`__)

* 'go_bp' (`Gene Ontology-Biological Process <http://geneontology.org/>`__)

* 'ctd_anat' (`CTD-Anatomy <http://ctdbase.org/>`__)

* 'uberon' (`UBERON ontology <http://obophenotype.github.io/uberon/>`__)

* 'go_cc' (`Gene Ontology-Cellular Component <http://geneontology.org/>`__)

* 'cell_ontology' (`Cell Ontology <https://cell-ontology.github.io/>`__)

* 'cellosaurus' (`Cellosaurus <https://www.cellosaurus.org/>`__)


After the pip installation, it is required a further step to install non-Python dependencies and to download the necessary data. Run in the command line:

::

   bent_setup


Only the default knowledge bases 'medic' and 'chebi' will be available at this point.


To disable annoyng messages in the terminal run:

::

   export TF_CPP_MIN_LOG_LEVEL='3'


You can download more knowledge bases later by specifying the desired knowledge bases among the ones that are available:

::

   python -c "from bent.get_kbs import get_additional_kbs;get_additional_kbs([<kb1>, <kb2>])"