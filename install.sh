#!/bin/bash
#MoonBrewCo Installer

confirmAnswer () {
whiptail --title "Confirmation" --yes-button "Yes" --no-button "No"  --defaultno --yesno "$1" 10 56
return $?
}

show_menu () {
  OPTION=$(whiptail --title "Welcome to MoonBrew" --menu "Choose your option:" 15 56 7 \
  "1" "Install MoonBrew" \
  "2" "Remove MoonBrew" \
  "3" "Restart MoonBrew" \
  "4" "Install No-IP" \
  "5" "Remove No-IP" \
  "6" "Reset MoonBrew Configuration" 3>&1 1>&2 2>&3)

  BUTTON=$?
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
        fi

        confirmAnswer "Do you want to add MoonBrew to autostart?"
        if [ $? = 0 ]; then
          sed "s,#DIR#,${PWD},g" MBC_service > /etc/systemd/system/MBC.service
          systemctl daemon-reload
          systemctl enable MBC
          systemctl start MBC
        fi
        whiptail --title "Installation Finished" --msgbox "MoonBrew installation finished! Click OK to continue." 8 78
        show_menu
        ;;

      2)
        confirmAnswer "Are you sure you want to remove MoonBrew?"
        if [ $? = 0 ]; then
          systemctl stop MBC
          systemctl disable MBC
          rm /etc/systemd/system/MBC.service
          rm /usr/lib/systemd/system/MBC.service
          systemctl daemon-reload
          systemctl reset-failed
        fi
        whiptail --title "Moon Brew Co. Removed" --msgbox "Moon Brew has been successfully removed. Click OK to continue." 8 78
        show_menu
        ;;

      3)
        systemctl restart MBC
        ipaddr=`ifconfig wlan0 2>/dev/null|awk '/inet addr:/ {print $2}'|sed 's/addr://'`
        whiptail --title "MoonBrew started" --msgbox "Please connect via Browser: http://$ipaddr:5000" 8 78
        show_menu
        ;;

      4)
        confirmAnswer "Are you sure you want to install the No-IP DUC?"
        if [ $? = 0 ]; then
          mkdir noip
          cd noip
          wget --content-disposition https://www.noip.com/download/linux/latest
          tar xf $(ls | head -n 1)
          cd $(ls | head -n 1)/binaries
          apt install ./$(ls | awk 'NR==2 {print}')
          cd ../../..
        fi

        confirmAnswer "Do you want to add No-IP to autostart?"
        if [ $? = 0 ]; then
          echo "Enter NoIP username:"
          read uname
          echo "Enter NoIP password:"
          read pswd
          cp ./noip/$(cd ./noip; ls | head -n 1)/debian/service /etc/systemd/system/noip-duc.service
          printf "NOIP_USERNAME=$uname\nNOIP_PASSWORD=$pswd\nNOIP_HOSTNAMES=moonbrew.ddns.net" > /etc/default/noip-duc
          systemctl daemon-reload
          systemctl enable noip-duc
          systemctl start noip-duc
        fi
        whiptail --title "No-IP DUC added" --msgbox "The No-IP DUC was succesfully added. Click OK to continue." 8 78
        show_menu
        ;;

      5)
        confirmAnswer "Are you sure you want to remove No-IP?"
        if [ $? = 0 ]; then
          rm -R noip
          apt remove noip-duc
        fi

        confirmAnswer "Are you sure you want to remove No-IP from autostart?"
        if [ $? = 0 ]; then
          systemctl stop noip-duc
          systemctl disable noip-duc
          rm /etc/systemd/system/noip-duc.service
          rm /usr/lib/systemd/system/noip-duc.service
          systemctl daemon-reload
          systemctl reset-failed
        fi
        whiptail --title "No-IP Removed" --msgbox "No-IP has been successfully removed. Click OK to continue." 8 78
        show_menu
        ;;

      6)
        confirmAnswer "Are you sure you want to delete the configuration file?"
        if [ $? = 0 ]; then
          rm -f config.txt
          whiptail --title "Config.txt Delted" --msgbox "The config file was succesfully deleted. Click OK to continue." 8 78
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