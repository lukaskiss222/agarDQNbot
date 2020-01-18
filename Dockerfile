FROM nikolaik/python-nodejs:python3.7-nodejs10

RUN apt-get update && yes|apt-get upgrade

RUN apt-get install vim sudo cmake libopenmpi-dev python3-dev zlib1g-dev -y \
    software-properties-common \
    unzip \
    curl \
    xvfb \
    x11-utils x11vnc


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




#Install neceserry packages for node
RUN npm install --global express uws@10.148.1


# Install the latest version of Geckodriver:
RUN BASE_URL=https://github.com/mozilla/geckodriver/releases/download \
  && VERSION=$(curl -sL \
    https://api.github.com/repos/mozilla/geckodriver/releases/latest | \
    grep tag_name | cut -d '"' -f 4) \
  && curl -sL "$BASE_URL/$VERSION/geckodriver-$VERSION-linux64.tar.gz" | \
    tar -xz -C /usr/local/bin


RUN pip install tensorflow==1.15 stable-baselines mss selenium gym pyvirtualdisplay

RUN adduser --disabled-password --gecos '' ubuntu && \
    adduser ubuntu sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 
USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod a+rwx /home/ubuntu/ && npm link uws express



