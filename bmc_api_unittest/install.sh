# clean
rm -rf /home/admin/api_unittest
rm -rf recovery/*

# backup
mv /usr/share/sonic/device/x86_64-alibaba_as* recovery/
cp -r /usr/local/etc/bmcutil.py recovery/

# patch
cp -r x86_64-alibaba_as* /usr/share/sonic/device/
cp bmcutil.py /usr/local/etc/

# install
sudo cp -r api_unittest /home/admin/api_unittest
