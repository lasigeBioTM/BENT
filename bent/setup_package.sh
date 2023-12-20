#!/bin/bash

root_path=$(python - <<END
import pkg_resources
package = pkg_resources.get_distribution('bent')
print(package.location)
END
)

package_path="${root_path}/bent"

echo $package_path


# ---------------------------------------------------------------------------
#                          Install utilities
# ---------------------------------------------------------------------------
apt-get update && apt-get upgrade

apt install wget
apt install git
apt install make

# ---------------------------------------------------------------------------
#                             Get and install JAVA
# ---------------------------------------------------------------------------
echo 'Installing JAVA...'
apt-get update && apt-get install -y default-jdk && apt-get autoclean -y

# ---------------------------------------------------------------------------
#    Retrieve Spacy model files
# ---------------------------------------------------------------------------
echo 'Retrieving Spacy model files...'
python_version=$(python -c 'import sys; print(sys.version_info[1])')

if [ "$python_version" -lt 10 ];then
    pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_lg-0.4.0.tar.gz


elif [ "$python_version" -ge 10 ];then
    pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_lg-0.5.3.tar.gz

fi
# ---------------------------------------------------------------------------
#            Download and prepare abbreviation detector AB3P
# ---------------------------------------------------------------------------
echo 'Downloading and preparing abbreviation detector AB3P...'

cwd=$(pwd)
mkdir "${package_path}/abbreviation_detector/"
cd "${package_path}/abbreviation_detector/"

git clone https://github.com/ncbi-nlp/NCBITextLib.git

# 1. Install NCBITextLib
cd NCBITextLib/lib/
make

cd ../../

## 2. Install Ab3P
git clone https://github.com/ncbi-nlp/Ab3P.git
cd Ab3P
sed -i 's/** location of NCBITextLib **/../NCBITextLib/' Makefile
make

cd $cwd

# ---------------------------------------------------------------------------
#           Eliminate annoying messages during Tensorflow execution
# ---------------------------------------------------------------------------
export TF_CPP_MIN_LOG_LEVEL='3'
export AUTOGRAPH_VERBOSITY='0'

# ---------------------------------------------------------------------------
#                   Download NILINKER and KB data
# ---------------------------------------------------------------------------

#cd $package_path

mkdir $package_path/data

# Download NILINKER, relations and entity frequency data
echo 'Downloading NILINKER, relations and entity frequency data...'
nil_script="${package_path}/get_data.sh"
chmod 755 $nil_script
bash $nil_script


# Download kb dicts
echo 'Downloading knowledge base dictionaries...'
mkdir $package_path/data/kbs/
kb_dir="${package_path}/data/kbs/dicts"
mkdir $kb_dir

kb_script="${package_path}/get_kb_dicts.sh"
chmod 755 $kb_script

kbs=('medic' 'chebi')

for kb in "${kbs[@]}"
do
    bash $kb_script $kb
done