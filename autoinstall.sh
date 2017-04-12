#!/bin/bash

PACOTES_APT="git alsa-utils mpg123 python-dev python-rpi.gpio python-pip";
PACOTES_PIP="pyfirmata";

DIRETORIO="~/luz-ciencia-emocao";
REPOSITORIO="sala-intensidade";
GITLINK="https://github.com/wsilverio/";

sudo apt-get update -y
sudo apt-get install -y $PACOTES_APT
sudo pip install $PACOTES_PIP

mkdir $DIRETORIO;
cd DIRETORIO;
git clone $GITLINK$REPOSITORIO.git;

# cd $REPOSITORIO;
# Iniciar com o boot
# python sala.py

# sudo modprobe snd_bcm2835
# sudo amixer cset numid=3 1
sudo raspi-config;
