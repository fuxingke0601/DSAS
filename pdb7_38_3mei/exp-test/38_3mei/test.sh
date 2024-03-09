#!/bin/bash


for file in a*; do
    cat $file
done

c=2
c=$(( $c + 2 ))
#miss_reflc=$(( ${all_reflc}-${obs_reflc}))

echo $c

current_dir=$(pwd)

# 将当前工作目录和文件名拼接起来，得到文件的绝对路径
name_1=$(ls shelx_*_ecal_cad_unique.mtz)
mtz="${current_dir}/${name_1}"

# 打印mtz变量的值
echo "The absolute path of mtz file is: $mtz"
