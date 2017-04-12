#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
TODO list:
    Heartbeat
    Progressão exponencial
    Audio
'''
import os, subprocess, sys, time
from multiprocessing import Process, Value

VOICE_FILE = './intensidade.mp3' # Localização do arquivo de voz

isRasp = True       # Raspberry Pi plataforma
hasFirmata = True   # Firmata modulo

MIN = 0             # PWM max
MAX = 255           # PWM min
STEP = 1            # PWM passo
DELAYMS = 10        # Delay (ms)

ARD_OUTPIN = 'd:3:p'    # Arduino pino

PI_INPIN = 7            # Raspberry pino (número no conector)
PI_LEDPIN = 11          # Raspberry pino (número no conector)

timeToExit = False

def pwmControl(board, out):
    if hasFirmata:
        for i in xrange(MIN, MAX, STEP):
            value = i/float(MAX)
            out.write(value)
            board.pass_time(delay)
            # print value
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
    tempo_ms = [50, 100, 15, 1200]
    toSeconds = lambda x: x/1000.0
    tempos = [toSeconds(i) for i in tempo_ms]

    while True:
                # GPIO.output(pin, GPIO.LOW)

        for i in xrange(0, len(tempos)):
            if (i % 2):
                if isRasp:
                    GPIO.output(pin, GPIO.LOW)
            else:
                if isRasp:
                    GPIO.output(pin, GPIO.HIGH)
                else:
                    print "*"
    
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

PORT = checkPort()  # Arduino porta ('/dev/ttyUSBx' or '/dev/ttyACMx')

i = 0
while PORT == None:
    print 'Nenhum dispositivo reconhecido em /dev/ttyACM* ou /dev/ttyUSB*'
    print 'Por favor, conecte um Arduino à porta USB {%d}\n' %i
    i += 1
    PORT = checkPort()
    time.sleep(5)

print 'Conectando a', PORT

ArduinoBoard = None
ArduinoPin = None

if hasFirmata:
    ArduinoBoard = Arduino(PORT)
    ArduinoPin = ArduinoBoard.get_pin(ARD_OUTPIN)

p = None
delay = DELAYMS/1000.0

# th=Thread(target=pwmControl, args=(ArduinoBoard, ArduinoPin,))
# th.start()

threadHeart = Process(target=heartBeat, args=(PI_LEDPIN,))
threadHeart.start()

try:
    while True:

        # heartBeat(PI_LEDPIN)
        # continue

        if isRasp:
            
            if GPIO.input(PI_INPIN) == 1: # Movimento detectado
                pass
        else:
            pass

        p = subprocess.Popen(['mpg123', '-q', VOICE_FILE])
        p.wait()
        # th.join()
        pwmControl(ArduinoBoard, ArduinoPin)

        # time.sleep(5)

except KeyboardInterrupt:
    threadHeart.terminate()

    if p != None:
        try:
            p.terminate()
        except OSError:
            pass # processo ja terminado
        except Exception as e:
            raise e

    if hasFirmata:
        try:
            ArduinoPin.write(0)
            ArduinoBoard.exit()
        except Exception as e:
            raise e

    if isRasp:
        GPIO.output(PI_LEDPIN, GPIO.LOW)
        GPIO.cleanup()

    exit()

except Exception as e:
    raise e
