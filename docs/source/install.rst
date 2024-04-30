Installation
============

To use the current version of BENT it is required: 

*  OS: Debian>=11/Ubuntu>=20.04

*  *  Python >=3.7, <=3.10.13

*  Required space between 5.5 GB - 10 GB 
   * Dependencies: 2.5 GB 
   * Data: between 3.0 GB (base) or 7.5 GB (if you use all available knowlegde bases for Named Entity Linking)


pip installation
~~~~~~~~~~~~~~~~

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

* 'fma' (`Foundation model of Anatomy <http://sig.biostr.washington.edu/projects/fm/AboutFM.html>`__)

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


Docker image
~~~~~~~~~~~~

If Docker is installed, you can pull BENT Docker image (~10 GB) from Docker hub and run a container.

Pull the Docker image:

::
   docker pull bent

Build the image in your working directory:

::
   docker build -t bent .


Then start a container using the built image. 


Get additional knowlegde bases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can download more knowledge bases later by specifying the desired knowledge bases among the ones that are available:

::

   python -c "from bent.get_kbs import get_additional_kbs;get_additional_kbs([<kb1>, <kb2>])"


Example: to download the NCBI Taxonomy and the NCBI Gene run: 

::

      python -c "from bent.get_kbs import get_additional_kbs;get_additional_kbs(['ncbi_taxon', 'ncbi_gene'])"

Alternatively, you can add your own knowledge base from text files (see 'Upload custom knowledge base/graph/ontology' in Usage)