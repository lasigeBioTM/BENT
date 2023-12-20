

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

*  OS: Debian>=11/Ubuntu>=20.04

*  Python >=3.7, <=3.10.13

*  Required space between 5.5 GB - 10 GB 
   * Dependencies: 2.5 GB 
   * Data: between 3.0 GB (base) or 7.5 GB (if you use all available knowledge bases for Named Entity Linking)

**NOTE**: Python Docker images (3.7 to 3.9) in `Docker Hub <https://hub.docker.com/_/python>`__ have Debian 11 as the base OS.


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


You can download more knowledge bases later by specifying the desired knowledge bases among the ones that are available:

::

   python -c "from bent.get_kbs import get_additional_kbs;get_additional_kbs([<kb1>, <kb2>])"


Example: to download the NCBI Taxonomy and the NCBI Gene run: 

::    

    python -c "from bent.get_kbs import get_additional_kbs;get_additional_kbs(['ncbi_taxon', 'ncbi_gene'])"


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
