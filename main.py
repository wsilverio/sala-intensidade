#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, subprocess, sys, time
from multiprocessing import Process, Value

VOICE_FILE = './intensidade.mp3' # Localização do arquivo de voz

isRasp = True       # Raspberry Pi plataforma
hasFirmata = True   # Firmata modulo

INTENSIDADES = 255  # Quantidade de valores de PWM entre 0->1
TEMPO_ENTRADA = 30  # Tempo (s) para começar a acender
TEMPO_SUBIDA = 15   # Tempo (s) para o PWM ir de 0->1
TEMPO_DESCIDA = 3   # Tempo (s) para o PWM ir de 1->0
TEMPO_SAIDA = 15    # Tempo (s) para o pessoal deixar a sala
EXP = 4             # Ajuste exponencial

UP = True
DOWN = False

ARD_OUTPINS = ['d:3:p', 'd:5:p', 'd:6:p', 'd:9:p', 'd:10:p', 'd:11:p'] # Arduino pinos

PI_INPIN = 7            # Raspberry pino (número no conector)
PI_LEDPIN = 11          # Raspberry pino (número no conector)

timeToExit = False

def pwmControl(board, outs, tempo, mode):
    if hasFirmata:
        for i in ( ((x/float(INTENSIDADES))**EXP) for x in range(1, INTENSIDADES+1) ):
            if mode == UP:
                for out in outs:
                    out.write(i)
            else:
                for out in outs:
                    out.write(1-i)
            
            board.pass_time(tempo/float(INTENSIDADES))
            
            if not isRasp:
                if mode == UP:
                    print i
                else:
                    print(1-i)
        
        if mode == DOWN:
            out.write(0)
    
def checkPort():
    port = None
    for file in os.listdir('/dev/'):
        if file.startswith('ttyACM') or file.startswith('ttyUSB'):
            port = os.path.join("/dev", file)
            break
            # PORT.append(os.path.join("/dev", file))
    return port

def heartBeat(pin):
    tempos = [i/1000.0 for i in [50, 100, 15, 1200]]

    while True:
        for i in xrange(0, len(tempos)):
            if (i % 2):
                GPIO.output(pin, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.HIGH)
    
            time.sleep(tempos[i])

try:
    from pyfirmata import Arduino, util
except ImportError:
    hasFirmata = False

if not hasFirmata:
    print "Módulo firmata não encontrado."

try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD) # Números dos pinos no conector
    GPIO.setup(PI_INPIN, GPIO.IN)
    GPIO.setup(PI_LEDPIN, GPIO.OUT)
    print "Plataforma: Raspberry Pi\n"
except ImportError:
    isRasp = False
    print "Plataforma: Não Raspberry Pi\n"

if isRasp:
    GPIO.output(PI_LEDPIN, GPIO.HIGH)

PORT = checkPort()  # Arduino porta ('/dev/ttyUSBx' or '/dev/ttyACMx')

i = 0
while PORT == None:
    print 'Nenhum dispositivo reconhecido em /dev/ttyACM* ou /dev/ttyUSB*'
    print 'Por favor, conecte um Arduino à porta USB {%d}\n' %i
    i += 1
    PORT = checkPort()
    time.sleep(5)

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

p = None
threadHeart = None

if isRasp:
    threadHeart = Process(target=heartBeat, args=(PI_LEDPIN,))
    threadHeart.start()

try:
    while True:

        playAudio = False

        if isRasp:
            if GPIO.input(PI_INPIN) == 1: # Movimento detectado
                playAudio = True
        else:
            playAudio = True

        if playAudio:
            p = subprocess.Popen(['mpg123', '-q', VOICE_FILE])
            
            time.sleep(TEMPO_ENTRADA)
            pwmControl(ArduinoBoard, ArduinoPins, TEMPO_SUBIDA, UP)
            
            time.sleep(50-TEMPO_SUBIDA-TEMPO_ENTRADA)
            pwmControl(ArduinoBoard, ArduinoPins, 3, DOWN)
            time.sleep(1)
            pwmControl(ArduinoBoard, ArduinoPins, 3, UP)
            time.sleep(1)
            pwmControl(ArduinoBoard, ArduinoPins, 3, DOWN)
            time.sleep(1)
            pwmControl(ArduinoBoard, ArduinoPins, 3, UP)
            time.sleep(1)
            
            p.wait()
            time.sleep(TEMPO_SAIDA)
            pwmControl(ArduinoBoard, ArduinoPins, TEMPO_DESCIDA, DOWN)

            time.sleep(5)

except Exception as e:

    if threadHeart != None:
        threadHeart.terminate()

    if p != None:
        try:
            p.terminate()
        except OSError:
            pass # processo ja terminado

    if hasFirmata:
        try:
            for pin in ArduinoPins:
                pin.write(0)
            
            ArduinoBoard.exit()
        except Exception:
            pass

    if isRasp:
        try:
            GPIO.output(PI_LEDPIN, GPIO.LOW)
            GPIO.cleanup()
        except Exception:
            pass

    raise e
