FROM node:10

RUN apt-get update && yes|apt-get upgrade

RUN apt-get install vim sudo cmake libopenmpi-dev python3-dev zlib1g-dev -y
RUN apt-get update && apt-get install -y \
    software-properties-common \
    unzip \
    curl \
    xvfb

RUN add-apt-repository "deb http://deb.debian.org/debian buster main" && apt-get update
RUN apt-get install -y x11-utils x11vnc





# Install the latest version of Firefox:
RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get install --no-install-recommends --no-install-suggests -y \
    # Firefox dependencies:
    libgtk-3-0 \
    libdbus-glib-1-2 \
    bzip2 \
  && DL='https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64' \
  && curl -sL "$DL" | tar -xj -C /opt \
  && ln -s /opt/firefox/firefox /usr/local/bin/ \
  && rm -rf \
    /tmp/* \
    /usr/share/doc/* \
    /var/cache/* \
    /var/lib/apt/lists/* \
    /var/tmp/*







# Install the latest version of Geckodriver:
RUN BASE_URL=https://github.com/mozilla/geckodriver/releases/download \
  && VERSION=$(curl -sL \
    https://api.github.com/repos/mozilla/geckodriver/releases/latest | \
    grep tag_name | cut -d '"' -f 4) \
  && curl -sL "$BASE_URL/$VERSION/geckodriver-$VERSION-linux64.tar.gz" | \
    tar -xz -C /usr/local/bin


RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod a+rwx /home/ubuntu/


RUN wget --progress=bar:force:noscroll https://repo.anaconda.com/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh
RUN bash Miniconda3-4.7.12.1-Linux-x86_64.sh -b && \
    echo "export PATH="/home/ubuntu/miniconda3/bin:$PATH"" >> ~/.bashrc && \
    /bin/bash -c "source ~/.bashrc"
RUN rm Miniconda3-4.7.12.1-Linux-x86_64.sh 

RUN git clone https://github.com/lukaskiss222/agarDQNbot 
WORKDIR /home/ubuntu/agarDQNbot
RUN git submodule update --init --recursive 

RUN npm install express && cd OgarII/ && npm install uws 

ENV PATH /home/ubuntu/miniconda3/bin:$PATH
RUN conda init bash
RUN conda env update -f configure.yml


