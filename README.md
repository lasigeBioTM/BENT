
## Installation

To use the current version of BENT it is required:
	:arrow_right: OS based on Ubuntu/Debian
	:arrow_right: [Conda](https://docs.conda.io/en/latest/) environment
	:arrow_right: Python>=3.7

Please ensure that you have the appropriate version of Conda installed.

Install the BENT package using pip through a terminal:

```
pip install bent
```

After the pip installation, it is required a further step to install non-Python dependencies and to download the necessary data:

```
python -c "from bent.setup_package import setup_package;setup_package()"
```

## Usage

BENT can be used for:
|:arrow_right:| Named Entity Recogniton (NER)
|:arrow_right:| Named Entity Linking (NEL)
|:arrow_right:| Named Entity Recognition and Linking (NER+NEL)


Access the full documentation [here]().