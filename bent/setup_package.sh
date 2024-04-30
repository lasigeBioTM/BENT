#!/bin/bash

package_path=$(find / -type d -name "bent" -print -quit)
echo 'The root package paths is' $package_path

# ---------------------------------------------------------------------------
#                          Install utilities
# ---------------------------------------------------------------------------
echo 'Installing apt utilities...'
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

#Find the python version installed in the system
pip_executable="$(which pip3)"

if [ -z "$pip_executable" ]; then
    pip_executable="$(which pip)"
fi

pip_command="$(basename "$pip_executable")"

for version in {10..7};do

    python_executable=$(which python3.${version})

    if [ -n python_executable ];then

        if [ "$version" -lt 10 ];then
            $pip_command install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_lg-0.4.0.tar.gz


        elif [ "$version" -eq 10 ];then
            $pip_command install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_lg-0.5.3.tar.gz
        
        break
        fi
    fi
done
# ---------------------------------------------------------------------------
#            Download and prepare abbreviation detector AB3P
# ---------------------------------------------------------------------------
echo 'Downloading and preparing abbreviation detector AB3P...'

cwd=$(pwd)
mkdir -p "${package_path}/abbreviation_detector/"
cd "${package_path}/abbreviation_detector/"

apt-get install g++

git clone https://github.com/ncbi-nlp/NCBITextLib.git

# 1. Install NCBITextLib
cd NCBITextLib/lib/
make

cd ../../

## 2. Install Ab3P
git clone https://github.com/ncbi-nlp/Ab3P.git
cd Ab3P
sed -i "s#\*\* location of NCBITextLib \*\*#../NCBITextLib#" Makefile
sed -i "s#\*\* location of NCBITextLib \*\*#../../NCBITextLib#" lib/Makefile
make

cd $cwd

# ---------------------------------------------------------------------------
#                   Download NILINKER and KB data
# ---------------------------------------------------------------------------

#cd $package_path

mkdir -p "${package_path}/data"

# Download NILINKER, relations and entity frequency data
echo 'Downloading NILINKER, relations and entity frequency data...'
nil_script="${package_path}/get_data.sh"
chmod 755 $nil_script
bash $nil_script $package_path


# Download kb dicts
echo 'Downloading knowledge base dictionaries...'
mkdir -p "${package_path}/data/kbs/"
kb_dir="${package_path}/data/kbs/dicts"
mkdir -p $kb_dir

kb_script="${package_path}/get_kb_dicts.sh"
chmod 755 $kb_script

kbs=('medic' 'chebi')

for kb in "${kbs[@]}"
do
    echo "Downloading ${kb} dictionaries..."
    bash $kb_script $package_path $kb
done