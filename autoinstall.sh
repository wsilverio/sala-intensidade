#!/bin/bash

PACOTES_APT="git alsa-utils mpg123 python-dev python-rpi.gpio python-pip";
PACOTES_PIP="pyfirmata";

DIRETORIO="$HOME/luz-ciencia-emocao";
REPOSITORIO="sala-intensidade";
GITLINK="https://github.com/wsilverio/";

echo -e "Atualizando o sistema..."
sudo apt-get update -y > /dev/null;
echo -e "Instalando pacotes..."
sudo apt-get install -y $PACOTES_APT > /dev/null;
echo -e "Instalando bibliotecas..."
sudo pip install $PACOTES_PIP > /dev/null;

echo -e "Removendo repositorio anterior..."
rm -rf $DIRETORIO;
mkdir -p $DIRETORIO;
cd DIRETORIO;
echo -e "Clonando novo repositorio..."
git clone $GITLINK$REPOSITORIO.git 2> /dev/null;

# cd $REPOSITORIO;
# Iniciar com o boot
# python sala.py

echo -e "Por favor, configure a saida de audio jack"
sudo raspi-config > /dev/null;

echo -e "Carregando modulo de audio..."
sudo modprobe snd_bcm2835 > /dev/null;
echo -e "Configurando saida de audio jack..."
sudo amixer cset numid=3 1 > /dev/null;
echo -e "Configurando volume 100%..."
amixer sset PCM,0 100% > /dev/null;

echo -e "Reiniciando o sistema..."
sudo reboot;