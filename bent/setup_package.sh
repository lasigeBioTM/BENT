#!/bin/bash

# ---------------------------------------------------------------------------
#                          Install utilities
# ---------------------------------------------------------------------------
conda install wget
conda install git
conda install make

# ---------------------------------------------------------------------------
#                             Get and install JAVA
# ---------------------------------------------------------------------------
#conda apt-get update
#apt-get install -y default-jdk 
#apt-get autoclean -y

#apt-get update && apt-get install -y default-jdk && apt-get autoclean -y

conda install -c conda-forge openjdk

# ---------------------------------------------------------------------------
#    Retrieve Spacy model files
# ---------------------------------------------------------------------------
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_lg-0.4.0.tar.gz

# ---------------------------------------------------------------------------
#            Download and prepare abbreviation detector AB3P
# ---------------------------------------------------------------------------

mkdir abbreviation_detector/
cd abbreviation_detector/

git clone https://github.com/ncbi-nlp/NCBITextLib.git

## 1. Install NCBITextLib
cd NCBITextLib/lib/
make

cd ../../

## 2. Install Ab3P
git clone https://github.com/ncbi-nlp/Ab3P.git
cd Ab3P
sed -i 's/** location of NCBITextLib **/../NCBITextLib/' Makefile
make

cd ../../

# ---------------------------------------------------------------------------
#           Eliminate annoying messages during Tensorflow execution
# ---------------------------------------------------------------------------
conda env config vars set TF_CPP_MIN_LOG_LEVEL='3'
conda env config vars set AUTOGRAPH_VERBOSITY='0'
#source ~/$1/etc/profile.d/conda.sh
#conda activate $CONDA_DEFAULT_ENV