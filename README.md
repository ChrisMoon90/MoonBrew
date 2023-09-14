Welcome to MoonBrew by Moon Brew Co. 

Backend Python3 server providing autonomous control for all grain brewing, fermentation & smokers. Compatible with Atlas Controls devices (temp, pH, etc.), Tilt hydrometers & up to 3ea solid state relays.


Required installation commands:


sudo apt update && sudo apt upgrade


CONFIRM HOW TO ADD PYTHON3 BLUEZ:
sudo apt-get install python3-bluez


NEED THIS TO ADD dbus_fast PATH TO SUPER USER:
sudo nano ~/.bashrc
ADD LINE: export PYTHONPATH=$PYTHONPATH:/usr/lib/python3.7/site-packages
source ~/.bashrc 
sudo visudo
ADD LINE: Defaults    env_keep += PYTHONPATH


NOT SURE IF I NEED THIS (ADDS PERMISSIONS TO P3.7 TO ACCESS fping?)
sudo setcap cap_net_raw+eip /usr/bin/python3.7

sudo pip3 install construct


pip3 install aiohttp[speedups]

pip3 install aiofiles (may not be needed)
pip install aiohttp_cors (may not be needed)


--  Chris Moon, PE
    Moon Brew Co.
