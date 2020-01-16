FROM node:10

RUN apt-get update && yes|apt-get upgrade
RUN apt-get install -y vim

RUN apt-get install sudo cmake libopenmpi-dev python3-dev zlib1g-dev -y
RUN apt-get update && apt-get install -y \
    software-properties-common \
    unzip \
    curl \
    xvfb

RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
RUN bash Anaconda3-5.0.1-Linux-x86_64.sh -b
RUN rm Anaconda3-5.0.1-Linux-x86_64.sh

RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod a+rwx /home/ubuntu/

RUN git clone https://github.com/lukaskiss222/agarDQNbot 
WORKDIR /home/ubuntu/agarDQNbot
RUN git submodule update --recursive

RUN conda env create -f configure.yml
RUN cd OgarII/ && npm install
RUN cd Cigar2/ && npm install

