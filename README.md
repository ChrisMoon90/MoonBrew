# Welcome to MoonBrew by Moon Brew Co. (V1.0)

Backend Python3 server providing autonomous control for all grain brewing, fermentation & smokers. Compatible with Atlas Controls devices (temp, pH, etc.), Tilt hydrometers & up to 3ea solid state relays.


## Installation
Open a terminal window on Raspberry Pi and type:

 <code>git clone https://github.com/Manuel83/craftbeerpi3</code>

This will download (clone) the software to your local Raspberry Pi.

Type <code>cd MoonBrew</code> to navigate into the MoonBrew folder.

Type <code>sudo ./install.sh</code>


## Misc Notes for Future Dev:

NEED THIS TO ADD pylibftdi TO SUPER USER:
sudo touch /etc/udev/rules.d/99-libftdi.rules
cd /etc/udev/rules.d
sudo nano 99-libftdi.rules
ADD:
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", GROUP="dialout", MODE="0660"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", GROUP="dialout", MODE="0660"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6011", GROUP="dialout", MODE="0660"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", GROUP="dialout", MODE="0660"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6015", GROUP="dialout", MODE="0660"

May also need to do the following:
sudo usermod -aG dialout $USER
sudo reboot

NEED THIS TO ADD dbus_fast PATH TO SUPER USER:
sudo nano ~/.bashrc
ADD LINE: export PYTHONPATH=$PYTHONPATH:/usr/lib/python3.7/site-packages
source ~/.bashrc 
sudo visudo
ADD LINE: Defaults    env_keep += PYTHONPATH

NOT SURE IF I NEED THIS (ADDS PERMISSIONS TO P3.7 TO ACCESS fping?)
sudo setcap cap_net_raw+eip /usr/bin/python3.7

mkdir /home/pi/noip
cd /home/pi/noip
wget https://www.noip.com/client/linux/noip-duc-linux.tar.gz
tar vzxf noip-duc-linux.tar.gz
cd noip-2.1.9-1
sudo make
sudo make install
sudo /usr/local/bin/noip2
sudo noip2 ­-S


--  Chris Moon, PE
    Moon Brew Co.
