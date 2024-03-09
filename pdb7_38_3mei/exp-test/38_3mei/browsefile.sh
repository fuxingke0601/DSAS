#!/bin/bash

file=$1

column_type=$( mtzdmp ${file} | grep -A2 "* Column Types :" |sed -n "3,3 p") #得到mtz文件中每一列的数据类型
filetitle=$(basename $1 | sed 's/...[az]$//g')
sg=$( mtzdmp ${file} -e| awk -F"'" '/Space group/{print $2}')                 #得到空间群信息
sg_1=$( echo ${sg} |tr -d ' ')
cell=$( mtzdmp ${file} | grep -A2 "* Cell Dimensions :" |sed -n "3,3 p")
reso=$( mtzdmp ${file} -e|grep -A2 "*  Resolution Range :" |sed -n "3,3 p" | awk '{printf $(NF-2)}')
#printf "$column_type $filetitle $sg $sg_1 $cell $reso \n"
# 要查找的字母
letter1="G"
letter2="L"
letter3="K"
letter4="M"

# 使用grep命令查找字母是否在文件的某一行中
if echo $column_type | grep -q ${letter1} && echo $column_type | grep -q ${letter2} ; then
	printf "F(+) SIGF(+) F(-) SIGF(-)  $cell $sg \n"
else 
	printf "I(+) SIGI(+) I(-) SIGI(-)  $cell $sg \n"
fi

