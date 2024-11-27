#!/bin/bash
#MoonBrewCo Installer

confirmAnswer () {
whiptail --title "Confirmation" --yes-button "Yes" --no-button "No"  --defaultno --yesno "$1" 10 56
return $?
}

show_menu () {
  # We show the host name right in the menu title so we know which Pi we are connected to
  OPTION=$(whiptail --title "MoonBrew 1.0" --menu "Choose your option:" 15 56 7 \
  "1" "Install MoonBrew" \
  "2" "Install No-IP" \
  "3" "Add MoonBrew to Autostart" \
  "4" "Remove MoonBrew from Autostart" \
  "5" "Start MoonBrew" \
  "6" "Stop MoonBrew" \
  "7" "Delete Configuration" 3>&1 1>&2 2>&3)

  BUTTON=$?
  # Exit if user pressed cancel or escape
  if [[ ($BUTTON -eq 1) || ($BUTTON -eq 255) ]]; then
      exit 1
  fi
  if [ $BUTTON -eq 0 ]; then
      case $OPTION in
      1)
          confirmAnswer "Would you like to run apt-get update & apt-get upgrade?"
          if [ $? = 0 ]; then
            apt-get -y update; apt-get -y upgrade;
          fi

          confirmAnswer "Install required python packages?"
          if [ $? = 0 ]; then
            echo "''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''"
            echo "Installing required Python3 modules..."
            python3 -m venv MBC-venv
            source MBC-venv/bin/activate
            pip3 install -r requirements.txt
            # sudo pip3 install -r requirements.txt
            # sudo cp -R /usr/lib/python3.7/site-packages/dbus_fast /usr/lib/python3.7
            # sudo cp -R /usr/lib/python3.7/site-packages/dbus_fast-1.86.0-py3.7.egg-info /usr/lib/python3.7
          fi

          confirmAnswer "Do you want to add MoonBrew to autostart?"
          if [ $? = 0 ]; then
            sed "s@#DIR#@${PWD}@g" MBC_boot > /etc/init.d/MBC_boot
            chmod 755 /etc/init.d/MBC_boot;
            update-rc.d MBC_boot defaults;
          fi

          whiptail --title "Installition Finished" --msgbox "MoonBrew installation finished! You must hit OK to continue." 8 78
          show_menu
          ;;

      2)
          confirmAnswer "Are you sure you want to install the No-IP DUC?"
          if [ $? = 0 ]; then
            uname="$(whoami)"
            echo $uname
            mkdir /home/$uname/noip
            cd /home/$uname/noip
            wget https://www.noip.com/client/linux/noip-duc-linux.tar.gz
            tar vzxf noip-duc-linux.tar.gz
            cd noip-2.1.9-1
            sudo make
            sudo make install
            sudo /usr/local/bin/noip2
            sudo noip2 -S
          fi

          confirmAnswer "Do you want to add No-IP to autostart?"
          if [ $? = 0 ]; then
             sed "s@#DIR#@${PWD}@g" noip_boot > /etc/init.d/noip_boot
             chmod 755 /etc/init.d/noip_boot;
             update-rc.d noip_boot defaults;
          fi

          whiptail --title "No-IP DUC added" --msgbox "The No-IP DUC was succesfully added. You must hit OK to continue." 8 78
          show_menu
          ;;

      3)
          confirmAnswer "Are you sure you want to add MoonBrew to autostart?"
          if [ $? = 0 ]; then
            sed "s@#DIR#@${PWD}@g" MBC_boot > /etc/init.d/MBC_boot
            chmod 755 /etc/init.d/MBC_boot;
            update-rc.d MBC_boot defaults;
            whiptail --title "MoonBrew added to autostart" --msgbox "MoonBrew was added to autostart succesfully. You must hit OK to continue." 8 78
          fi
          show_menu
          ;;

      4)
          confirmAnswer "Are you sure you want to remove MoonBrew from autostart?"
          if [ $? = 0 ]; then
            update-rc.d -f MBC_boot remove
          fi
          show_menu
          ;;

      5)
          sudo /etc/init.d/MBC_boot start
          ipaddr=`ifconfig wlan0 2>/dev/null|awk '/inet addr:/ {print $2}'|sed 's/addr://'`
          whiptail --title "MoonBrew started" --msgbox "Please connect via Browser: http://$ipaddr:5000" 8 78
          show_menu
          ;;

      6)
          sudo /etc/init.d/MBC_boot stop
          whiptail --title "MoonBrew stoped" --msgbox "The software is stoped" 8 78
          show_menu
          ;;

      7)
        confirmAnswer "Are you sure you want to delete the configuration file?"
        if [ $? = 0 ]; then
          sudo rm -f config.txt
          whiptail --title "Config.txt Delted" --msgbox "The config file was succesfully deleted. You must hit OK to continue." 8 78
        fi
        show_menu
        
       esac
   fi
}

if [ "$EUID" -ne 0 ]
  then whiptail --title "Error" --msgbox "Please run the install file as root user -> sudo bash install.sh " 8 78
  exit
fi

show_menu