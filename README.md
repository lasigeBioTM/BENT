# BENT: Biomedical Entity Annotator

Python package for Named Entity Recognition (NER) and Linking (NEL) in the biomedical domain.

NER models are based on [PubMedBERT](https://arxiv.org/pdf/2007.15779.pdf) and a post-processing rule-based module.
the NEL model is a graph-based approach based on the Personalized PageRank algorithm and Information content.

Access the full documentation [here](https://bent.readthedocs.io/en/latest/).

Citation:

```
@article{RUAS2022104137,
title = {NILINKER: Attention-based approach to NIL Entity Linking},
journal = {Journal of Biomedical Informatics},
volume = {132},
pages = {104137},
year = {2022},
issn = {1532-0464},
doi = {https://doi.org/10.1016/j.jbi.2022.104137},
url = {https://www.sciencedirect.com/science/article/pii/S1532046422001526},
author = {Pedro Ruas and Francisco M. Couto},
keywords = {Biomedical text, Named Entity Linking, Knowledge Bases, Natural language processing, Neural networks, Text mining},
abstract = {The existence of unlinkable (NIL) entities is a major hurdle affecting the performance of Named Entity Linking approaches, and, consequently, the performance of downstream models that depend on them. Existing approaches to deal with NIL entities focus mainly on clustering and prediction and are limited to general entities. However, other domains, such as the biomedical sciences, are also prone to the existence of NIL entities, given the growing nature of scientific literature. We propose NILINKER, a model that includes a candidate retrieval module for biomedical NIL entities and a neural network that leverages the attention mechanism to find the top-k relevant concepts from target Knowledge Bases (MEDIC, CTD-Chemicals, ChEBI, HP, CTD-Anatomy and Gene Ontology-Biological Process) that may partially represent a given NIL entity. We also make available a new evaluation dataset designated by EvaNIL, suitable for training and evaluating models focusing on the NIL entity linking task. This dataset contains 846,165 documents (abstracts and full-text biomedical articles), including 1,071,776 annotations, distributed by six different partitions: EvaNIL-MEDIC, EvaNIL-CTD-Chemicals, EvaNIL-ChEBI, EvaNIL-HP, EvaNIL-CTD-Anatomy and EvaNIL-Gene Ontology-Biological Process. NILINKER was integrated into a graph-based Named Entity Linking model (REEL) and the results of the experiments show that this approach is able to increase the performance of the Named Entity Linking model.}
}
```

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
