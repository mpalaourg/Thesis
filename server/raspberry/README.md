# Database host until VM is up
> Embedded System used	-> Raspberry Pi 0.

## Setup Connectivity with Raspberry Pi
First, download Raspbian Image from [**here (lite version)**](https://www.raspberrypi.org/downloads/raspberry-pi-os). Then, enable ssh (off by default) and add the network details to the Raspberry Pi, as described [**here**](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md). 
Open the ```wpa-supplicant``` configuration file in nano:
```sh
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
Go to the bottom of the file and add the following:
```sh
network={
    ssid=<MyNetworkSSID>
    psk=<MySuperSecretNetworkPassword>
}
```
Finnaly, reconfigure the interface with ```wpa_cli -i wlan0 reconfigure```.

## Connect with Raspberry Pi
To conenct with the Raspberry Pi, SSH via WiFi will be used. To find your local ip assigned to Raspberry, you can use an app (i.e [**Fing**](https://play.google.com/store/apps/details?id=com.overlook.android.fing&hl=en)) or if you are already connected via USB with the Raspberry, you can use
```sh
ifconfig wlan0
```
and check the assigned IP. Then, from your PC you can run

```sh
ssh pi@LOCAL_IP
<MySuperSecretSSHPassword>
```

## Setup Raspberry Pi
First, transfer the Server file to Raspberry.
```sh
scp Server.py pi@LOCAL_IP:~
```
Then, install the dependecies for the server script (Python3 is needed, with pip3) and the Database
```sh
sudo pip3 install Flask
sudo pip3 install pymongo==3.4.0
sudo pip3 install waitress
sudo apt install -y mongodb
```

## Run Server Script
To run the server script even when we aren't connected with the Raspberry ```screen``` will be used. You can check if it is installed on your system by typing:
```sh
screen --version
```
If you don’t have ```screen``` installed on your system, you can easily install it using the package manager of your distro.
```sh
sudo apt install screen
```
Start, a new screen session via
```sh
screen -S sessionName
```
Inside the session, run the server script with:
```sh
python3 Server.py &
```
To minimize this session, use ```Ctrl+a Ctrl+d``` and to reattach with the linux screen ``` screen -r ```. Finally, to list all the active linux screens use ``` screen -ls```.

## Backup the database
Inside Raspberry, run:
```sh
mongodump -d mydb
```
Then, transfer it to your PC (for Windows you must enable [**OpenSSH**](https://winscp.net/eng/docs/guide_windows_openssh_server#on_windows_10_version_1803_and_newer)) by running:
```
scp -r dump PC_USER@PC_LOCALIP:/your/desired/path/.
```

## Network IP Changes
[**NoIp**](https://my.noip.com/#!/) will be used. The files will be sent to a hostname, where (even when my ip changes) they will be redirect to my Public IP. Finally, by Port Forwarding the files will be redirected to the Local IP of my Raspberry.
