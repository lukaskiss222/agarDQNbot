# agar DQN BOT

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

I have created a Agar Discreate Env enviroment, which can be used to create any type of RL Bot. The main framework is used the  [stable-baselines](https://github.com/hill-a/stable-baselines) and it used to implement DQN bot for this game. (Stable baselines implement many other RL algoritms, so fell free to try them on this project.)

## The idea of Enviroment
Our whole enviroment is build upon gym enviroment. At the initialization of the enviroment, both server and client of Agar are started. Step function returns number of frames, which was specified at the initialization. (This is necesery, because then out agent can recognize movement direction.) 


## Enviroment
The enviroment is based on two github repositories, both have little changes. 
- Server side - Fork of [OgarII](https://github.com/Luka967/OgarII) - DQN requires discretize space, so we discretize the server with command *next_step*. 
- Client side - This client side is fork from [CigarII](https://github.com/Cigar2/Cigar2). We added some *input hidden* fields to index.html. These *input fields* are used fro communication between our python agent and server. 


We use [selenium](https://selenium-python.readthedocs.io/) to run webrowser and connect to our local webserver, which connects to Agar server.

Both server and client are coded in javascript, which is necessery to install.

At each step (also includes the reset step) multiple screeshots are taken of the opened selenium webrowser and return as the enviroment state.

Deatiled enviroment description can be find below.

### Agar server settings
You can modify the world by editing _settings.json_ file. 
They are multiple options you can play with as:

-
-
-



## Installation

### Docker Instalation (recomanded)
Download the git files and submodules
```bash
git clone https://github.com/lukaskiss222/agarDQNbot
cd agarDQBbot/
git submodule update --init --recursive
```
Install docker
```bash
docker pull scriptus/agarbot:latest
```
Run the docker with bash 
```
docker run --rm -it -p 5900:5900 -p 6006:6006 -v $PWD:/home/agarDQNbot scriptus/agarbot /bin/bash 
```

#### How to see the training 
If you want to see the enviroment then run training in the background by:
```bash
python main.py &
./connect_to_training.sh :1001
```
The last command will open xvfb to vnc port 5900 of your docker.
Then on your localhost computer just run:
```bash
vncviewer  :0
```
and the window with the game should appear.
#### Testing model
If you want to test your model run:
```bash
python test_model.py models/<model>.zip &
./connext_to_training.sh :1001
```
as before run in yout local host vncviewer
### Locahost instalation
#### Install Node and NPM
- Dependencies 
```bash
sudo apt-get install curl
curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash -
sudo apt-get install nodejs
sudo apt-get update && sudo apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev
```
Clone the project
```bash
git clone https://github.com/lukaskiss222/agarDQNbot
git submodule update --recursive
```

The selenium module requires [*geckodriver*](https://github.com/mozilla/geckodriver/releases).
Download it from *https://github.com/mozilla/geckodriver/releases* and untar it and copy it to */usr/bin/*.



Install our python enviroment:
```bash
conda env create -f configure.yml
conda activate agarBot
```
Also we need to install necessery NPM **packages** to our client and server.
```bash
cd OgarII/
npm install
cd ../Cigar2/
npm install
cd ..
```
Check with this command, if everuthing is insstalled properly:
```bash
python EnviromentAgar.py
```


Somethimes node server is left running, so use ***killall node*** to kill server or client

## Training
Run 
```bash
python main.py
```

### Detail enviroment description
- At the initialization of our gym enviroment, the *Client webserver* and *agar webserver* are started by subprocess and are left running until you close the gym enviroment. It is not recommended to multiple instances of our gym enviroment. (They will overlap. Moreover, you can not run mutiple servers on the same port.)
- .......


## Help
Any help is welcome, this project is a answer to HW for machine learning class. 


## To do (Coming soon, hopefully :D)


- [ ] Future development
  - [x] Moving enviroment to stable-baselines? (Maybe My DQN agent is not working) 
  - [ ] Create own client based on Ws socket
    * Instead of images, it will get just server info by sockets
    * Maybe applicatble to normal Agar servers
