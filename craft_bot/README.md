# Setting up a project

0. Install Python 2.7 and pip

1. Install MongoDB
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
sudo echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list #for Ubuntu 16.04
sudo apt-get update
sudo apt-get install -y mongodb-org
```

2. install 'python-telegram-bot'
```
pip install python-telegram-bot --upgrade
```

3. Install 'pymongo'
```
pip install pymongo
```