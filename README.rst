

BENT: Biomedical Entity Annotator
---------------------------------

Python Library for Named Entity Recogntion (NER) and Linking (NEL) in the biomedical domain.

NER models are based on `PubMedBERT <https://arxiv.org/pdf/2007.15779.pdf>`__ and a post-processing rule-based module.
the NEL model is a graph-based approach based on the Personalized PageRank algorithm and Information content.

BENT can be used for: 

* Named Entity Recogniton (NER)
* Named Entity Linking (NEL) 
* Named Entity Recognition and Linking (NER+NEL)

Access the full documentation `here <ffgdf>`__.

Citation:

* Pedro Ruas and Francisco M. Couto. `Nilinker: attention-based approach to nil entity linking <https://www.sciencedirect.com/science/article/pii/S1532046422001526>`__. Journal of Biomedical Informatics, 132:104137, 2022. doi: https://doi.org/10.1016/j.jbi.2022.104137.

Installation
~~~~~~~~~~~~

To use the current version of BENT it is required: 

* OS based on Ubuntu/Debian 
* `Conda <https://docs.conda.io/en/latest/>`__ environment 
* Python>=3.7
* 22 GB free space

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


After the pip installation, it is required a further step to install non-Python dependencies and to download the necessary data:

::

   python -c "from bent.setup_package import setup_package;setup_package()"

Reinitiate the conda environment.





