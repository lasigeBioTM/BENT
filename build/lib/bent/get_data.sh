#!/bin/bash

root_path=$(python - <<END
import pkg_resources
package = pkg_resources.get_distribution('bent')
print(package.location)
END
)

package_path="${root_path}/bent"

# ---------------------------------------------------------------------------
#                    Create directories for later use
# ---------------------------------------------------------------------------
data_dir="${package_path}/data"
cd $data_dir

mkdir $data_dir/datasets/
mkdir $data_dir/NILINKER/


#-------------------------------------------------------------------------
#   Download entity frequency dicts (to resolve overlapping entities)
#-------------------------------------------------------------------------
gdown https://drive.google.com/uc?id=1PYk84F_eCRYgbZ1c8VMCH9srKqulF0AV
tar -xvf overlapping_entities.tar.gz
rm overlapping_entities.tar.gz

#--------------------------------------------------------------------------
# Download dictionaries with relations
#-------------------------------------------------------------------------- 
gdown https://drive.google.com/uc?id=1wDfQkyF526d6FBAbjZlmbrcWsMrUzfdL
tar -xvf relations.tar.gz
rm relations.tar.gz

#-------------------------------------------------------------------------
#                       Download NILINKER data
#-------------------------------------------------------------------------
cd $data_dir/NILINKER/
# Word-concept dictionaries
wget https://zenodo.org/record/6561477/files/word_concept.tar.gz?download=1
tar -xvf 'word_concept.tar.gz?download=1'
rm 'word_concept.tar.gz?download=1'

# Trained models files
wget https://zenodo.org/record/6561477/files/nilinker_files.tar.gz?download=1
tar -xvf 'nilinker_files.tar.gz?download=1'
rm 'nilinker_files.tar.gz?download=1'

# Embeddings
wget https://zenodo.org/record/6561477/files/embeddings.tar.gz?download=1
tar -xvf 'embeddings.tar.gz?download=1'
rm 'embeddings.tar.gz?download=1'

cd ../