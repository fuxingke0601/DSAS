#!/bin/bash

python_evn="/home/fuxingke/anaconda3/envs/dsas_python3_10/bin/python"

cd /ssd2/code_python/pythonProject/pdb7_38_3mei/exp-test/38_3mei

sayr=1
mtz_rel="prasa_5oq2_2.61_unique.mtz"
if [ $# == 13 ];then
   mtz=$1
   sayr=$2
   scut=$3
   ntri=$4
   nitr=$5
   reso=$6
   weak=$7
   bp3=$8
   cctr=$9
   number_heavyatom=${10}
   type_heavyatom=${11}
   wavelegth=${12}
   mtz_rel=${13}  #include F+ F-
else
   echo "eg: $0 shelx_3mei-sf_ecal_cad_unique.mtz 1 1000 400 498 2.11 0.48 0 0.5428 2 Br 0.912 3mei-sf.mtz"
   exit
fi

rm -r file*.txt CC_400.txt recover*

#peak_search more 2 atoms
c=$(( $c + 2 ))

echo "$mtz_rel"
#mtz_init=$(readlink -f ${mtz_rel})
#mtz=${mtz_rel}

echo "$mtz"

./CF_run.sh ${mtz} ${weak} ${scut} ${cctr} ${reso} ${sayr} ${ntri} ${nitr} .


#peak_search more 2 atoms
num_atom=$(( ${number_heavyatom} + 2 ))

echo "#############################"

for file in recover*.mtz; do
    ./zpeak_cal.sh ${file} ${num_atom} ${type_heavyatom} ${bp3} ${wavelegth} ${mtz_rel}
done

echo "DSAS completed successfully"
