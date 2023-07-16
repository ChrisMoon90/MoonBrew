Welcome to MoonBrew by Moon Brew Co. 

Backend Python3 server providing autonomous control for all grain brewing, fermentation & smokers. Compatible with Atlas Controls devices (temp, pH, etc.), Tilt hydrometers & up to 3ea solid state relays.

Auto installation instructions to come.

Required Python3 libraries:

sudo apt-get install python3-bluez
or
sudo apt install pkg-config libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev python-dev
pip3 install gattlib
pip3 install pybluez[ble]
or
pip3 install pybluez

sudo setcap cap_net_raw+eip /usr/bin/python3.7


--  Chris Moon, PE
    Moon Brew Co.
