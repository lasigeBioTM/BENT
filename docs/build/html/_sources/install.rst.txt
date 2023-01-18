Installation
============

To use the current version of BENT it is required: 

|:arrow_right:| Ubuntu/Debian based OS

|:arrow_right:| `Conda <https://docs.conda.io/en/latest/>`__ environment 

|:arrow_right:| Python>=3.7

|:arrow_right:| 22 GB free space

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