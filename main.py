#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################################
### Módulos
######################################################################
import os, subprocess, sys, time
from multiprocessing import Process, Value

######################################################################
### Globais
######################################################################
VOICE_FILE = './intensidade.mp3' # Localização do arquivo de voz

isRasp = True       # Raspberry Pi plataforma
hasFirmata = True   # Firmata modulo

INTENSIDADES = 255  # Quantidade de valores de PWM entre 0->1
TEMPO_ENTRADA = 30  # Tempo (s) para começar a acender
TEMPO_SUBIDA = 15   # Tempo (s) para o PWM ir de 0->1
TEMPO_DESCIDA = 3   # Tempo (s) para o PWM ir de 1->0
TEMPO_SAIDA = 15    # Tempo (s) para o pessoal deixar a sala
EXP = 4             # Ajuste exponencial

UP = True		# subida PWM
DOWN = False	# descida PWM

# Arduino pinos: usa todas as saídas PWM, ou seja, o mosfet pode ser conectado a qualquer pino '~'
ARD_OUTPINS = ['d:3:p', 'd:5:p', 'd:6:p', 'd:9:p', 'd:10:p', 'd:11:p']

PI_INPIN = 7            # Sensor: Raspberry pino (número no conector)
PI_LEDPIN = 11          # LED informativo: Raspberry pino (número no conector)

# timeToExit = False	# flag de saida (não mais necessária?)

######################################################################
### Funcao PWM
######################################################################
def pwmControl(board, outs, tempo, mode):
    if hasFirmata:
    	# 'i' variando entre 0->1 de forma exponencial
        for i in ( ((x/float(INTENSIDADES))**EXP) for x in range(1, INTENSIDADES+1) ):
            if mode == UP:
                # escreve em todas as saídas
                for out in outs:
                    out.write(i)
            else: # == DOWN
            	# escreve em todas as saídas
                for out in outs:
                    out.write(1-i)
            
            board.pass_time(tempo/float(INTENSIDADES)) # delay
            
            # apenas imprime os valores (DEBUG)
            if not isRasp:
                if mode == UP:
                    print i
                else:
                    print(1-i)
        
        if mode == DOWN:
            out.write(0) # apaga o led após a variação exponencial

######################################################################
### Retorna o endereço da porta USB do Arduino
######################################################################    
def checkPort():
    port = None
    for file in os.listdir('/dev/'):
        if file.startswith('ttyACM') or file.startswith('ttyUSB'):
            port = os.path.join("/dev", file)
            break # sai da função ao encontrar o primeiro dispositivo
            
            # PORT.append(os.path.join("/dev", file))
    
    return port

######################################################################
### Thread para piscar o LED informativo (DEBUG)
######################################################################
def heartBeat(pin):
    tempos = [i/1000.0 for i in [50, 100, 15, 1200]]
    while True:
        for i in xrange(0, len(tempos)):
            if (i % 2):
                GPIO.output(pin, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.HIGH)
    
            time.sleep(tempos[i])

######################################################################
### Inicialização
######################################################################

### Verifica se o módulo Firmata está instalado
try:
    from pyfirmata import Arduino, util
except ImportError:
    hasFirmata = False

if not hasFirmata:
    print "Módulo firmata não encontrado."

### Verifica se o programa está sendo rodado num Raspberry Pi
try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)		# Números dos pinos no conector
    GPIO.setup(PI_INPIN, GPIO.IN) 	# sensor
    GPIO.setup(PI_LEDPIN, GPIO.OUT)	# LED informativo
    print "Plataforma: Raspberry Pi\n"
except ImportError:
    isRasp = False
    print "Plataforma: Não Raspberry Pi\n"

if isRasp:
    GPIO.output(PI_LEDPIN, GPIO.HIGH)	# Acende o LED informativo

PORT = checkPort()	# Verifica se há algum Arduino conectado ('/dev/ttyUSBx' ou '/dev/ttyACMx')

### Aguarda até que o Arduino seja conectado à porta USB
i = 0 # flag para a mensagem
while PORT == None:
    print 'Nenhum dispositivo reconhecido em /dev/ttyACM* ou /dev/ttyUSB*'
    print 'Por favor, conecte um Arduino à porta USB {%d}\n' %i
    i += 1
    PORT = checkPort()	# nova checagem
    time.sleep(5)		# delay

### Inicializa a conexão com o Arduino
ArduinoBoard = None
ArduinoPins = []

if hasFirmata:
    try:
        print 'Conectando a', PORT
        ArduinoBoard = Arduino(PORT)

        for pin in ARD_OUTPINS:
            ArduinoPins.append(ArduinoBoard.get_pin(pin))
            
    except Exception as e:
        print "Não foi possível conectar."
        raise e
    else:
        print "Conectado."

### Lança a thread do LED informativo (DEBUG)
threadHeart = None # thread

if isRasp:
    threadHeart = Process(target=heartBeat, args=(PI_LEDPIN,))
    threadHeart.start()

######################################################################
### Loop infinito
######################################################################
p = None # subprocesso (audio)

try:
    while True:

        playAudio = False

        if isRasp:
            if GPIO.input(PI_INPIN) == 1: # Movimento detectado
                playAudio = True
        else: # DEBUG
            playAudio = True

        if playAudio:
            p = subprocess.Popen(['mpg123', '-q', VOICE_FILE]) # reproduz o áudio
            
            time.sleep(TEMPO_ENTRADA) # luz apagada durante o tempo de entrada
            pwmControl(ArduinoBoard, ArduinoPins, TEMPO_SUBIDA, UP) # acende a luz (exponencial)
            
            ### alterna a luz (acende - apaga)
            time.sleep(50-TEMPO_SUBIDA-TEMPO_ENTRADA)
            pwmControl(ArduinoBoard, ArduinoPins, 3, DOWN)
            time.sleep(1)
            pwmControl(ArduinoBoard, ArduinoPins, 3, UP)
            time.sleep(1)
            pwmControl(ArduinoBoard, ArduinoPins, 3, DOWN)
            time.sleep(1)
            pwmControl(ArduinoBoard, ArduinoPins, 3, UP)
            time.sleep(1)
            
            p.wait() # aguarda o término do áudio
            time.sleep(TEMPO_SAIDA) # tempo para que o pessoal deixa a sala
            pwmControl(ArduinoBoard, ArduinoPins, TEMPO_DESCIDA, DOWN) # apaga a luz

            time.sleep(5) # delay para nova checagem do sensor

### comando de saída ou algum problema no loop principal
except Exception as e:

    # encerra a thread do led informativo
    if threadHeart != None:
        threadHeart.terminate()

    if p != None:
        try:
            # encerra o audio
            p.terminate()
        except OSError:
            pass # processo ja terminado

    if hasFirmata:
        try:
            # apaga a(s) luz(es)
            for pin in ArduinoPins:
                pin.write(0)
            
            # desconecta o Arduino
            ArduinoBoard.exit()
        except Exception:
            pass

    if isRasp:
        try:
            # apaga o LED informativo e libera as GPIO
            GPIO.output(PI_LEDPIN, GPIO.LOW)
            GPIO.cleanup()
        except Exception:
            pass

    raise e
