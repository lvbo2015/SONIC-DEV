# clean
if [ -e /home/admin/api_unittest ];then
    rm -rf /home/admin/api_unittest
fi

if [ -d recovery ];then
    rm -rf recovery/*
else
    if [ -f recovery ];then
        rm recovery
    fi
    mkdir recovery
fi

# backup
mv /usr/share/sonic/device/x86_64-alibaba_as* recovery/
cp -r /usr/local/etc/bmcutil.py recovery/

# patch
cp -r x86_64-alibaba_as* /usr/share/sonic/device/
cp bmcutil.py /usr/local/etc/

# install
sudo cp -r api_unittest /home/admin/api_unittest
