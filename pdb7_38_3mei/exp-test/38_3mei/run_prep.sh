#!/bin/bash

python_evn="/home/fuxingke/anaconda3/envs/dsas_python3_10/bin/python"

cd /ssd2/code_python/pythonProject/pdb7_38_3mei/exp-test/38_3mei

sayr=1
mtz_rel="prasa_5oq2_2.61_unique.mtz"
if [ $# == 8 ];then
   mtz_rel=$1
   sayr_bool=$2
   scut=$3
   ntri=$4
   nitr=$5
   reso=$6
   weak=$7
   bp3=$8
else
   echo "eg: $0 3mei-sf.mtz 1 1000 400 498 2.11 0.48 0"
   exit
fi

echo "$mtz_rel"
#mtz_init=$(readlink -f ${mtz_rel})
mtz=${mtz_rel}
echo "$mtz"
#####################################################################################
######################################calc shelx freeflag############################
#####################################################################################
if [ -d "mtz_prep" ];then
   rm -r mtz_prep
fi
mkdir mtz_prep
cp $mtz prep.sh mtz_prep
cd mtz_prep
./prep.sh $mtz

####################################calc resolution#########################
if (( $(echo "${reso} < 0.1" | bc) ));then
   reso=$($python_evn ../reso_cal.py shelxC.log shelx_ecal_cad.mtz)
fi

#判断shelx_${filetitle}_ecal_cad_unique.mtz是否存在，如果存在把它拷到主路径里
shopt -s nullglob

if [ ! -e shelx_*_ecal_cad_unique.mtz ];then
        echo "no shelx_ecal_cad_unique file"
	exit
else
	current_dir=$(pwd)
	mtz=$(ls shelx_*_ecal_cad_unique.mtz)
	mtz_shelxc_abs="${current_dir}/${mtz}"
fi

rm ../shelx_*_ecal_cad_unique.mtz
cp shelx_*_ecal_cad_unique.mtz ..
cd ..

#####################################################################################
######################################calc cctr######################################
#####################################################################################
cctr=$($python_evn cctr_cal.py $mtz)
####################################################################################
#####################################calc nitr######################################
####################################################################################
if (( $(echo "${nitr} < 0.1" | bc) ));then

nitr=498
#reso=3
if (( $(echo "${reso} > 3.8" | bc) ));then
   nitr=748
else
   nitr=498
fi

fi

#echo "${nitr} ${reso}"

#####################################################################################
######################################calc weak######################################
#####################################################################################
if (( $(echo "${weak} < 0.1" | bc) ));then

if [ -d "para_test_0.2" ] || [ -d "para_test_0.3" ] || [ -d "para_test_0.4" ] || [ -d "para_test_0.5" ];then
   rm -r  para_test_*
fi
weak1=0.5
weak2=0.4
weak3=0.3
weak4=0.2
mkdir para_test_${weak1}
mkdir para_test_${weak2}
mkdir para_test_${weak3}
mkdir para_test_${weak4}

echo "../${mtz} ${weak1} 1300 ${cctr} ${reso} 0 10 ${nitr}"
parallel ::: "cd para_test_${weak1}; ../CF_run.sh ../${mtz} ${weak1} 1300 ${cctr} ${reso} 0 10 ${nitr} .. >log_${weak1}.txt" \
	     "cd para_test_${weak2}; ../CF_run.sh ../${mtz} ${weak2} 1300 ${cctr} ${reso} 0 10 ${nitr} .. >log_${weak2}.txt" \
	     "cd para_test_${weak3}; ../CF_run.sh ../${mtz} ${weak3} 1300 ${cctr} ${reso} 0 10 ${nitr} .. >log_${weak3}.txt" \
	     "cd para_test_${weak4}; ../CF_run.sh ../${mtz} ${weak4} 1300 ${cctr} ${reso} 0 10 ${nitr} .. >log_${weak4}.txt"
######从log文件中得到卡完分辨率后观测到的衍射点数目和总衍射点数目
all_reflc=$(cat para_test_0.2/log_0.2.txt | awk -F":" '/Reading MTZ completed,total reflections/{print $2}')
obs_reflc=$(cat para_test_0.2/log_0.2.txt | awk -F":" '/not missing reflections :/{print $2}')
miss_reflc=$(( ${all_reflc}-${obs_reflc}))
echo "dsdsssd"
echo "$all_reflc $obs_reflc $c"

weak1_nan=$($python_evn nan_cal.py para_test_${weak1}/log_${weak1}.txt)
weak2_nan=$($python_evn nan_cal.py para_test_${weak2}/log_${weak2}.txt)
weak3_nan=$($python_evn nan_cal.py para_test_${weak3}/log_${weak3}.txt)
weak4_nan=$($python_evn nan_cal.py para_test_${weak4}/log_${weak4}.txt)
#weak1_nan=4
#weak2_nan=4
#weak3_nan=4
#weak4_nan=0
#echo "$weak1_nan $weak2_nan $weak3_nan $weak4_nan"

num_count_array=($weak1_nan $weak2_nan $weak3_nan $weak4_nan)
weak_array=(${weak1} ${weak2} ${weak3} ${weak4})
first_num=3
for num_cunt in 0 1 2 3
do
   if [ ${num_count_array[num_cunt]} -lt 3 ];then
      first_num=${num_cunt}
      break
   fi
done

second_num=$((${first_num}+1))
#echo "$first_num $second_num"

weak=0.5
if [ ${first_num} -lt 3 ];then
   if [ ${num_count_array[first_num]} -gt 0 ] && [ ${num_count_array[second_num]} == 0 ];then
      weak=$(printf "%.2f" `echo "${weak_array[first_num]}-0.05" | bc` )
   elif [ ${num_count_array[first_num]} -gt 0 ] && [ ${num_count_array[second_num]} -gt 0 ];then
      weak=$(printf "%.2f" `echo "${weak_array[first_num]}-0.15" | bc` )
   elif [ ${num_count_array[first_num]} == 0 ];then
      weak=$(printf "%.2f" `echo "${weak_array[first_num]}-0.02" | bc` )
   else
      weak=$(printf "%.2f" `echo "${weak_array[first_num]}-0.02" | bc` )
   fi
else
   if [ ${num_count_array[first_num]} -gt 2 ];then
      weak=$(printf "%.2f" `echo "${weak_array[first_num]}-0.12" | bc` )
   elif [ ${num_count_array[first_num]} -gt 0 ] && [ ${num_count_array[first_num]} -lt 3 ];then
      weak=$(printf "%.2f" `echo "${weak_array[first_num]}-0.05" | bc` )
   else
      weak=${weak_array[first_num]}
   fi

fi


fi
#rm -r para_test_*

#####################################################################################
######################################calc scut######################################
#####################################################################################
if (( $(echo "${scut} < 0.1" | bc) ));then

scut=1300
if [ ${obs_reflc} -lt 2001 ];then
   scut=500
elif [ ${obs_reflc} -lt 5001 ] && [ ${obs_reflc} -gt 2000 ];then
   scut=1000
elif [ ${obs_reflc} -lt 8000 ] && [ ${obs_reflc} -gt 5000 ];then
   scut=1300
else 
   scut=1500
fi

fi

#####################################################################################
######################################calc ntri######################################
#####################################################################################
if (( $(echo "${ntri} < 0.1" | bc) ));then
   ntri=400
fi

#####################################################################################
######################################calc sayr######################################
#####################################################################################


echo "cmtz:  1111 ${mtz_shelxc_abs} 2222"
echo "sayr:  ${sayr}"
echo "scut:  ${scut}"
echo "ntri:  ${ntri}"
echo "nitr:  ${nitr}"
echo "reso:  ${reso}"
echo "weak:  ${weak}"
echo " bp3:  ${bp3}"
echo "cctr:  ${cctr}"

#./CF_run.sh ${mtz} ${weak} ${scut} ${cctr} ${reso} ${sayr} 400 ${nitr} .
