#!/bin/bash

rmalogpath="/tmp/logAll"
bmclogdir="/tmp/bmcLogAll"
soniclogdir="/tmp/sonicLogAll"

bmcloglist=("/var/log/syslog"
	    "/var/log/syslog.1"
	    '/var/log/syslog.[2-9].gz'
	    "/var/log/console_syslog.log"
	    "/var/log/console_syslog.log.1"
	    "/var/log/console_syslog.log.[2-9].gz"
	    "/var/log/cpumon.log"
	    "/var/log/fand.log"
	    "/var/log/dcdcmon.log"
	    "/var/log/powermon.log"
	    "/mnt/data/autodump.tar.gz"
	    "/var/log/autodump/autodump.tar.gz")

sonicloglist=("/var/log/syslog"
	    "/var/log/syslog.1"
	    '/var/log/syslog.[2-19].gz'
	    "/var/log/swss/sairedis.rec"
	    "/var/log/swss/sairedis.rec.1"
	    "/var/log/swss/sairedis.rec.[2-19].gz"
	    "/var/log/swss/swss.rec"
	    "/var/log/swss/swss.rec.1"
	    "/var/log/swss/swss.rec.[2-19].gz"
	    "/var/log/bmc/bmc_console.log"
	    "/var/log/bmc_feed_watchdog.log"
	    "/var/log/kern.*")

bmcloglistN=()
sonicloglistN=()


arrayExtend(){
	#echo "bmc srcArr is: ${bmcloglist[@]}"
	for (( i = 0 ; i < ${#bmcloglist[@]} ; i++ ))
	do
		#echo "${bmcloglist[$i]}"
		str=`echo "${bmcloglist[$i]}" | grep -oE "[0-9]+\-[0-9]+"`
		if [ $str ]; then
			a=`echo $str |cut -d "-" -f1`
			b=`echo $str |cut -d "-" -f2`
			for((j=$a;j<=$b;j++)){
				bmcloglistN[${#bmcloglistN[*]}]=`echo "${bmcloglist[$i]}" | sed -r "s/\[[0-9]+\-[0-9]+\]/$j/"`
			}
		else
			bmcloglistN[${#bmcloglistN[*]}]=${bmcloglist[$i]}
		fi
	done
	#echo ${bmcloglistN[*]}

	#echo "sonic srcArr is: ${sonicloglist[@]}"
	for (( i = 0 ; i < ${#sonicloglist[@]} ; i++ ))
	do
		#echo "${sonicloglist[$i]}"
		str=`echo "${sonicloglist[$i]}" | grep -oE "[0-9]+\-[0-9]+"`
		if [ $str ]; then
			a=`echo $str |cut -d "-" -f1`
			b=`echo $str |cut -d "-" -f2`
			for((j=$a;j<=$b;j++)){
				sonicloglistN[${#sonicloglistN[*]}]=`echo "${sonicloglist[$i]}" | sed -r "s/\[[0-9]+\-[0-9]+\]/$j/"`
			}
		else
			sonicloglistN[${#sonicloglistN[*]}]=${sonicloglist[$i]}
		fi
	done
	#echo ${sonicloglistN[*]}
}

scpFileFromBmc(){
	expect -c "
	#spawn scp -r root@240.1.1.1:$1 $2
	spawn sudo scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@240.1.1.1:$1 $2
	expect {
		\"*assword\" { set timeout 300; send \"0penBmc\r\"; exp_continue; }
		\"yes/no\" { send \"yes\r\"; }
	}"
}

bmcLogCollect(){
	echo "BMC log collect ..."

	if [ -d $bmclogdir ]; then
		rm -rf $bmclogdir
	fi
	mkdir -p $bmclogdir

	for file in ${bmcloglistN[@]}
	do
		#echo "$file"
		scpFileFromBmc $file $bmclogdir
	done
}

sonicLogCollect(){
	echo "SONiC log collect ..."

	if [ -d $soniclogdir ]; then
		rm -rf $soniclogdir
	fi
	mkdir -p $soniclogdir

	for file in ${sonicloglistN[@]}
	do
		if [ -f $file ]; then
			#echo "$file"
			cp $file $soniclogdir
		fi
	done
}

checkfile(){
	echo "BMC log file check exist test ..."
	for file in ${bmcloglist[@]}
	do
		echo $file
		if ssh root@240.1.1.1 test -e $file; then
			echo "$file exist"
		fi
	done

}


arrayExtend
echo  "bmcloglist:"
for line in ${bmcloglistN[*]}; do
	echo $line
done

echo ""
echo "sonicloglist:"
for line in ${sonicloglistN[*]}; do
	echo $line
done


bmcLogCollect
sonicLogCollect

rmalogdir=`echo $rmalogpath | awk -F "/" '{print $NF}'`

if [ -d $rmalogpath ]; then
	rm -rf $rmalogpath
fi

if [ -f $rmalogpath.tar.gz ]; then
	rm -rf $rmalogpath.tar.gz
fi

mkdir -p $rmalogpath
mv $bmclogdir $rmalogpath
mv $soniclogdir $rmalogpath

cd /tmp
tar -zcf $rmalogdir.tar.gz $rmalogdir
rm -rf $rmalogpath
