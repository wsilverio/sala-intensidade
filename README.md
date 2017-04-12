##### TODO list:
- PCB
- Instalador automático
	- git clone, diretório
- Lançar o programa no boot
- Heartbeat	
- Documentação
- Placa conversor de nível (sensor)

### Arduino IDE:

##### Carregando o firmware do Arduino

* Abrir o sketch [Standard Firmata](https://github.com/firmata/arduino/blob/master/examples/StandardFirmata/StandardFirmata.ino):
`File >> Examples >> Firmata >> StandardFirmata`

* Selecionar placa:
`Tools >> Board >> Arduino/Genuino UNO`

* Selecionar microcontrolador:
`Tools >> Processor >> ATmega328`

* Gravar o sketch:
`Sketch >> Upload`

### Raspberry Pi:

##### Preparando o cartão de memória

* Baixar a última versão do [Raspbian](https://www.raspberrypi.org/downloads/raspbian/).

* Gravar a imagem (.img) com o [Etcher](https://etcher.io/).

* Montar a partição `boot` e habilitar a conexão ssh:
```bash
cd /media/user/boot # (obs: o endereço pode ser outro)
touch ssh
```

##### Configurando o Raspberry Pi
* Inserir o cartão de memória e conectar os cabos de alimentação e rede.

* Acessar o Raspberry Pi:
```bash
ssh pi@raspberrypi # (obs: o IP ou hostname pode ser outro)
pass: raspberry
```

* Executar o instalador automático (este passo pode levar alguns minutos):
```bash
bash <(curl -s https://raw.githubusercontent.com/wsilverio/sala-intensidade/master/autoinstall.sh)
```

* Configurar a saída de áudio (**obs: sem reiniciar o sistema**):
`Advanced Options >> Audio >> Force 3.5mm ('headphone') jack >> Ok`
`Finish >>  Would you like to reboot now? >> No`  

* Adicionar a seguinte linha ao crontab:
`@reboot cd /home/pi/luz-ciencia-emocao/sala-intensidade/ && python sala.py`

* O sistema reiniciará automaticamente  