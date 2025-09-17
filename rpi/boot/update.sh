#!/bin/bash

#get IP address
IP=$(hostname -I)
DATE=$(date)

# if there is a network connection

# log all IPs with sed?? 
echo "$DATE IP Address is $IP" >> ~/cs334/rpi/boot/ip.md
# what's the actual file name lol & get the ip thru grep?????
echo "$IP" >> ~/cs334/rpi/boot/ip.md
echo "1" >> ~/cs334/rpi/boot/ip.md

# copy the config files over
cp -r ~/.config configcopy

git add .
git commit -m "update IP address"
git push origin
