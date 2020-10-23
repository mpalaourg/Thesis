#!/bin/sh
# backup.sh
# navigate to home directory, create a variable with the current date to append to the file name
# and take a backup of mydb transfered to my PC.

cd /
cd home/pi/
today=`date '+%Y_%m_%d__%H_%M_%S'`
filename="/home/pi/dump-$today"
echo $filename
mongodump -d mydb -o $filename > backup.log
echo Done with the backup!
scp -r $filename user@192.168.100.5:/Users/user/Desktop/backup/. >> backup.log
echo Done with the transfer!
rm -r $filename
