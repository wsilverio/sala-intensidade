#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
TODO list:
'''
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

ARD_OUTPIN = 'd:3:p'    # Arduino pino

PI_INPIN = 7            # Raspberry pino (número no conector)
PI_LEDPIN = 13          # Raspberry pino (número no conector)

timeToExit = False

def pwmControl(board, out, tempo, mode):
    if hasFirmata:
        for i in ( ((x/float(INTENSIDADES))**EXP) for x in range(1, INTENSIDADES+1) ):
            if mode == UP:
                out.write(i)
            else:
                out.write(1-i)
            board.pass_time(tempo/float(INTENSIDADES))
            # if not isRasp:
            #     print i
        
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
        if not isRasp:
            print ""
        for i in xrange(0, len(tempos)):
            if (i % 2):
                if isRasp:
                    GPIO.output(pin, GPIO.LOW)
            else:
                if isRasp:
                    GPIO.output(pin, GPIO.HIGH)
                else:
                    print "*"
    
            try:
                time.sleep(tempos[i])
            except Exception:
                break

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

PORT = checkPort()  # Arduino porta ('/dev/ttyUSBx' or '/dev/ttyACMx')

i = 0
while PORT == None:
    print 'Nenhum dispositivo reconhecido em /dev/ttyACM* ou /dev/ttyUSB*'
    print 'Por favor, conecte um Arduino à porta USB {%d}\n' %i
    i += 1
    PORT = checkPort()
    time.sleep(5)

ArduinoBoard = None
ArduinoPin = None

if hasFirmata:
    try:
        print 'Conectando a', PORT
        ArduinoBoard = Arduino(PORT)
        ArduinoPin = ArduinoBoard.get_pin(ARD_OUTPIN)
    except Exception as e:
        print "Não foi possível conectar."
        raise e
    else:
        print "Conectado."

p = None

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
            # time.sleep(5)
            p = subprocess.Popen(['mpg123', '-q', VOICE_FILE])
            time.sleep(TEMPO_ENTRADA)
            pwmControl(ArduinoBoard, ArduinoPin, TEMPO_SUBIDA, UP)
            p.wait()
            time.sleep(TEMPO_SAIDA)
            pwmControl(ArduinoBoard, ArduinoPin, TEMPO_DESCIDA, DOWN)


except Exception as e:

    threadHeart.terminate()

    if p != None:
        try:
            p.terminate()
        except OSError:
            pass # processo ja terminado

    if hasFirmata:
        try:
            ArduinoPin.write(0)
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
