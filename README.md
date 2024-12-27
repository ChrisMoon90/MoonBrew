# Welcome to MoonBrew by Moon Brew Co.

Python3 server providing autonomous control for all grain brewing, fermentation & smokers. Compatible with Atlas Controls devices (temp, pH, etc.), Tilt hydrometers & up to 3ea solid state relays.


## Version 2.3

Updates to installer to fix RPi5 username issues and adds Python virtual environment for libraries.
Updates to Actors module to replace RPi.GPIO with gpiod to resolve GPIO compatability with RPi5.


## Installation

Open a terminal on Raspberry Pi and navigate to <code>/home/'username'</code>

Type <code>git clone https://github.com/ChrisMoon90/MoonBrew.git</code>

This will download (clone) the software to your local Raspberry Pi.

Type <code>cd MoonBrew</code> to navigate into the MoonBrew folder.

Type <code>sudo bash ./install.sh</code>

Follow the prompts to install MoonBrew dependencies.

Note: do not forget to enable I2C and Serial Port in the RPi Configuration menu.


## External Antenna:

To add external antenna funcationality for CM5, modfy the boot config file:

<code>sudo nano /boot/firmware/config.txt</code>

Add the following to the end of the file:

<code># Switch to external antenna
dtparam=ant2
</code>

## 

--  Chris Moon, PE
    Moon Brew Co.
