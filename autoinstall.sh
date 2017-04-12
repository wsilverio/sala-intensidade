#!/bin/bash

PACOTES_APT="git alsa-utils mpg123 python-dev python-rpi.gpio python-pip";
PACOTES_PIP="pyfirmata";

DIRETORIO="~/luz-ciencia-emocao";
REPOSITORIO="sala-intensidade";
GITLINK="https://github.com/wsilverio/";

echo -e "Atualizando o sistema..."
sudo apt-get update -y > /dev/null;
echo -e "Instalando pacotes..."
sudo apt-get install -y $PACOTES_APT > /dev/null;
echo -e "Instalando pacotes bibliotecas..."
sudo pip install $PACOTES_PIP > /dev/null;

mkdir $DIRETORIO;
cd DIRETORIO;
echo -e "Clonando o repositorio remoto..."
git clone $GITLINK$REPOSITORIO.git > /dev/null;

# cd $REPOSITORIO;
# Iniciar com o boot
# python sala.py

echo -e "Por favor, configure a saida de audio jack:"
echo -e "\tAdvanced Options"
echo -e "\tAudio"
echo -e "\tForce 3.5mm ('headphone') jack"
echo -e "\tOk"
echo -e ""
echo -e "Finish" 
echo -e "\tWould you like to reboot now?"
echo -e "\tNo"
sudo raspi-config;

echo -e "Carregando modulo de audio..."
sudo modprobe snd_bcm2835 > /dev/null;
echo -e "Configurando saida de audio jack..."
sudo amixer cset numid=3 1 > /dev/null;
echo -e "Configurando volume 100%..."
amixer sset PCM,0 100% > /dev/null;

echo -e "Reiniciando o sistema..."
sudo reboot;