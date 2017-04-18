##### TODO list:
- **Verificar alimentação Arduino - cabo USB / 12V**

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
cd /media/$USER/boot # (obs: o endereço pode ser outro)
touch ssh
```

##### Configurando o Raspberry Pi
* Inserir o cartão de memória e conectar os cabos de alimentação e rede.

* Acessar o Raspberry Pi:
```bash
ssh pi@raspberrypi # (obs: usuário, IP ou hostname podem ser outros)
pass: raspberry
```

* Executar o instalador automático (este passo pode levar alguns minutos):
```bash
bash <(curl -s https://raw.githubusercontent.com/wsilverio/sala-intensidade/master/autoinstall.sh)
```

* Configurar a saída de áudio (**obs: sem reiniciar o sistema**):  
`Advanced Options >> Audio >> Force 3.5mm ('headphone') jack >> Ok`  
`Finish >>  Would you like to reboot now? >> No`  

* O sistema reiniciará automaticamente.  
* O programa se iniciará automaticamente nos próximos boots.  

##### Obtento a última versão do projeto
* Sempre que houver uma nova atualização do projeto:
```bash
bash <(curl -s https://raw.githubusercontent.com/wsilverio/sala-intensidade/master/autoinstall.sh)
```
