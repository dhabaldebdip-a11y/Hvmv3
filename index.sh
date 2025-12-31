#!/bin/bash

while true; do
clear

echo -e "\e[36m"
echo "FlashNodes Hosting Manager"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 GodXtreme HOSTING MANAGER"
echo "made by GodXtreme"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "__  __    _    ___ _   _    __  __ _____ _   _ _   _"
echo "|  \/  |  / \  |_ _| \ | |  |  \/  | ____| \ | | | | |"
echo "| |\/| | / _ \  | ||  \| |  | |\/| |  _| |  \| | | | |"
echo "| |  | |/ ___ \ | || |\  |  | |  | | |___| |\  | |_| |"
echo "|_|  |_/_/   \_\___|_| \_|  |_|  |_|_____|_| \_|\___/"
echo -e "\e[0m"

echo ""
echo "1) Change Root Password"
echo "2) Coming Soon"
echo "3) Exit"
echo ""
read -p "Select option [1-3]: " opt

case $opt in
  1)
    passwd
    ;;
  2)
    echo "🚧 We Are Working On It!"
    sleep 2
    ;;
  3)
    echo "👋 Bye!"
    exit 0
    ;;
  *)
    echo "❌ Invalid Option"
    sleep 1
    ;;
esac
done
