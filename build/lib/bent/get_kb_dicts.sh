#!/bin/bash

root_path=$(python - <<END
import pkg_resources
package = pkg_resources.get_distribution('bent')
print(package.location)
END
)

package_path="${root_path}/bent"

cd ${package_path}/data/kbs/dicts/

target_kb=$1

if [ $target_kb = 'medic' ]
then
    download_url='https://drive.google.com/uc?id=1Q0SYp0NBOEg5hUUS-Gu1tdBfQvJx5Wax'

elif [ $target_kb = 'cellosaurus' ]
then
    download_url='https://drive.google.com/uc?id=1M2KSW0w8l0KXcmdntgdslxOwV8kturvh'

elif [ $target_kb = 'chebi' ]
then
    download_url='https://drive.google.com/uc?id=1Var1gzVrKghH07NWdPFC2re-AgSZaIFD'

elif [ $target_kb = 'cl' ]
then
    download_url='https://drive.google.com/uc?id=1xRnOI6roERKQzvzzmDfvBh3R5PGAsw7r'

elif [ $target_kb = 'ctd_anat' ]
then
    download_url='https://drive.google.com/uc?id=1zsR1EaoVgE-jlEkSxvv_NRip8BOQTkEX'

elif [ $target_kb = 'ctd_chem' ]
then
    download_url='https://drive.google.com/uc?id=1I4GFLtK994i4dfANPiG4li_ETlrxQvHd'

elif [ $target_kb = 'ctd_gene' ]
then
    download_url='https://drive.google.com/uc?id=1Mj97VK5b_MT-n-gj_k23tvOYZhxG_l71'

elif [ $target_kb = 'do' ]
then
    download_url='https://drive.google.com/uc?id=1wkoeQ4VtGoBUGOLuIHO1mB5g5gAV5LPr'

elif [ $target_kb = 'go_bp' ]
then
    download_url='https://drive.google.com/uc?id=1Zgt_QaAaE9O0wWErof8o_Kxb5PFQmT00'

elif [ $target_kb = 'go_cc' ]
then
    download_url='https://drive.google.com/uc?id=1qBL-vd9DY83CGyKvxvAN58IPSTfODvKH'

elif [ $target_kb = 'ncbi_taxon' ]
then
    download_url='https://drive.google.com/uc?id=1vor5Ba6p3DtmDLhQP3qQkXofCcIZLHpC'

elif [ $target_kb = 'uberon' ]
then
    download_url='https://drive.google.com/uc?id=1H_sP93uEkrjerdbCX0VqoPsZ_lBiua17'

elif [ $target_kb = 'ncbi_gene' ]
then
    download_url='https://drive.google.com/uc?id=1dVJbSZYzTtkE6_v6eAQ4UNzQLtVWITLE'

elif [ $target_kb = 'fma' ]
then
    download_url='https://drive.google.com/uc?id=1v_Kyi7mFg9hD8thaawd6ASNpwQSiix0N'

fi

gdown $download_url
tar -xvf $target_kb.tar.gz
rm $target_kb.tar.gz


cd ../../