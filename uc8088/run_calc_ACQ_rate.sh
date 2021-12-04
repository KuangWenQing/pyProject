#!/bin/bash

calc_aqc_success_rate()
{
	# grep "ACQ EFF" $1 | awk -F  '[ ,]' '{sum+=$5} END {print "Sum = ", sum}'
	sum=`grep -a "ACQ EFF" $1 | awk -F  '[ ,]' '{sum+=$5} END {print sum}'`
	sum_eff=$((10#${sum}))

	tail_acq_eff=`grep -an "ACQ EFF" $1 | tail -1`
	tail_acq_eff_row_num=$((10#${tail_acq_eff%%:*}))
	
	pli_str=`grep -an "pli a:" $1 | tail -1`
	pli_str_row_num=$((10#${pli_str%%:*}))
	
	sum_pli=0

	if (( $tail_acq_eff_row_num < $pli_str_row_num ))
	then
		comma_num=`echo $pli_str | awk -F',' '{print (NF-1)}'`
	
		if [ $comma_num -eq 9 ]
		then
		#	echo $pli_str
			sum=`echo $pli_str | awk -F'100' '{print 10-(NF-1)}'`
		else
			echo comma_num=$comma_num , so use Previous pli_str
			pli_str=`grep -a "pli a:" $1 | tail -2 | head -1`
		#	echo $pli_str
			sum=`echo $pli_str | awk -F'100' '{print 10-(NF-1)}'`
		fi
		
		sum_pli=$((10#${sum}))
		#echo pli not equate 100 total =  $sum_pli
	fi
	sum=$(($sum_eff+$sum_pli))
	echo sum = $sum
	
	acq_num=`grep -a "ACQ SP" $1 | wc -l`
	echo acq_num = $acq_num
	echo sum / acq_num = $(printf "%.5f" `echo "scale=5;$sum/$acq_num"|bc`)
}


if [ $# -ne 0  ]; then
    if [ -d $1 ]
    then
	echo 'dir'
	old_path=`pwd`
	cd $1
	for f in `ls *.log`
	do
		path_name=$1/$f
		echo -e "\n" $path_name
		/home/ucchip/KWQ/code/py/pyProject/uc8088/calc_acq_time.py $path_name
		calc_aqc_success_rate $path_name
	done
	cd $old_path
	exit
    fi

    while [ $# != 0 ]
    do
        echo -e "\n"    $1		
		/home/ucchip/KWQ/code/py/pyProject/uc8088/calc_acq_time.py $1
		calc_aqc_success_rate $1
        shift
    done
else
    echo "Usage: \"./run.sh path_file\"";
    exit
fi

