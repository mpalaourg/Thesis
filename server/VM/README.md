# Server and Database hosting 
> Virtual Machine	in okeanos.grnet.gr -> `Ubuntu 16.04.3 LTS`

## Connect to VM

The connection is established via ssh:
```sh
ssh user@VM_IP
<MySuperSecretSSHPassword>
```

---

## Setup Virtual Machine
First, transfer the Server file to the VM.
```sh
scp Server.py user@VM_IP:~
```
Then, install the dependecies for the server script (Python3 is needed, with pip3) and the [<b>Database</b>](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
```sh
sudo pip3 install Flask
sudo pip3 install waitress
sudo pip3 install pymongo
sudo pip3 install requests
sudo apt-get install -y mongodb-org
```

---

## Setup Database
Run mongo without privileges from localhost (VM), to create the admin user `<ADMIN_USER>`
```sh
mongo
use admin
db.createUser(
  {
    user: <ADMIN_USER>,
    pwd: <MONGO_ADMIN_USER_PASSWORD>,
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
```
Connect to `<ADMIN_USER>` via
```sh
mongo --port <MONGO_PORT> -u <ADMIN_USER> -p <MONGO_ADMIN_USER_PASSWORD> --authenticationDatabase "admin"
```
and check the user connected with
```sh
db.runCommand( {connectionStatus: 1})
```
We will use this user to generate the low priviliges user `<MONGO_USER>`. Then, create a database `<AUTH_DB>` for holding `<MONGO_USER>` permissions.
```sh
use <AUTH_DB>
```
Create user `<MONGO_USER>` (connected as `<ADMIN_USER>`)
```sh
db.createUser(
  {
    user: <MONGO_USER>,
    pwd: <MONGO_USER_PASSWORD>,
    roles: [ { role: "readWrite", db: <DB_NAME> } ]
  }
)
```
Connect to `<MONGO_USER>` via
```sh
mongo --port <MONGO_PORT> -u <MONGO_USER> -p <MONGO_USER_PASSWORD> --authenticationDatabase <AUTH_DB>
```
To have users with roles, we must enable security at `/etc/mongod.conf`
```sh
sudo nano /etc/mongod.conf
```
In this file add the following lines:
```sh
  security:
    authorization: 'enabled'
```
Finally, restart mongo service
```sh
sudo service mongod restart
```

---

## Run Server Script
To run the server script even when we aren't connected with the VM ```screen``` will be used. You can check if it is installed on your system by typing:
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

---

## Backup the database
Activate remote access, by modifying `/etc/mongod.conf`
```sh
sudo nano /etc/mongod.conf
```
In this file modify the following lines:
```sh
  net:
    port: <MONGO_PORT>
    bindIp: 0.0.0.0   #default value is 127.0.0.1
```
Restart mongo service
```sh
sudo service mongod restart
```
and from your PC run:
```sh
mongodump --uri="mongodb://<MONGO_USER>:<MONGO_USER_PASSWORD>@<VM_IP>:<MONGO_PORT>/<DB_NAME>?authSource=<AUTH_DB>" -o your/desired/path/.
```
