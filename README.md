# BENT: Biomedical Entity Annotator

Python package for Named Entity Recognition (NER) and Linking (NEL) in the biomedical domain.

NER models are based on [PubMedBERT](https://arxiv.org/pdf/2007.15779.pdf) and a post-processing rule-based module.
the NEL model is a graph-based approach based on the Personalized PageRank algorithm and Information content.

Access the full documentation [here](https://bent.readthedocs.io/en/latest/).

Citation:


> Pedro Ruas, Francisco M. Couto. [NILINKER: Attention-based approach to NIL Entity Linking](https://www.sciencedirect.com/science/article/pii/S1532046422001526). Journal of Biomedical Informatics, Volume 132, 2022. ISSN 1532-0464. https://doi.org/10.1016/j.jbi.2022.104137.


## Installation

To use the current version of BENT it is required:

:arrow_right: OS based on Ubuntu/Debian

:arrow_right: [Conda](https://docs.conda.io/en/latest/) environment

:arrow_right: Python>=3.7

:arrow_right: 22 GB free space


Please ensure that you have the appropriate version of Conda installed.

Create a Conda environment (adapt for the name of your project):

```
conda create --name annotation_project python=3.7
```

Activate the environment:

```
conda activate annotation_project
```

Install the BENT package using pip through a terminal:

```
pip install bent
```

After the pip installation, it is required a further step to install non-Python dependencies and to download the necessary data:

```
python -c "from bent.setup_package import setup_package;setup_package()"
```

Reinitiate the conda environment.


## Usage

BENT can be used for:

:arrow_right: Named Entity Recogniton (NER)

:arrow_right: Named Entity Linking (NEL)

:arrow_right: Named Entity Recognition and Linking (NER+NEL)


Access the full documentation [here](https://bent.readthedocs.io/en/latest/).
