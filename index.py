import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep, time
import signal
import sys
import csv
from negados import Negados
from permitidos import Permitidos

GPIO.setmode(GPIO.BOARD)
ledVerde = 8
ledVermelho = 10
buzzer = 12

GPIO.setup(ledVerde, GPIO.OUT)
GPIO.setup(ledVermelho, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)

leitorRfid = SimpleMFRC522()

autorizacoes = Permitidos()
negacoes = Negados()

tempoEntrada = {}
tentativasNegadas = {}
tentativasInvasao = 0

def tocarBuzzer(freq, duracao):
    pwm = GPIO.PWM(buzzer, freq)
    pwm.start(50)
    sleep(duracao)
    pwm.stop()

def salvarRelatorio():
    with open('relatorio.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Colaborador", "Tempo Total (horas)", "Tentativas Negadas", "Tentativas de Invasão"])
        
        for tag, tempos in tempoEntrada.items():
            nome = autorizacoes.get(tag, "Desconhecido")
            tempoTotal = sum([saida - entrada for entrada, saida in tempos if saida is not None]) / 3600
            writer.writerow([nome, f"{tempoTotal:.2f}", tentativasNegadas.get(nome, 0), tentativasInvasao])

        for tag, nome in negacoes.items():
            if tag not in tempoEntrada:
                writer.writerow([nome, "0.00", tentativasNegadas.get(nome, 0), tentativasInvasao])

        writer.writerow(["Invasão Desconhecida", "N/A", "N/A", tentativasInvasao])

def finalizar(signal, frame):
    print("\nTodos os acessos:")
    for tag, tempos in tempoEntrada.items():
        nome = autorizacoes[tag]
        tempoTotal = sum([saida - entrada for entrada, saida in tempos if saida is not None])
        print(f"{nome} ficou {tempoTotal / 3600:.2f} horas na sala.")
    
    print("\nTentativas negadas:")
    for nome, tentativas in tentativasNegadas.items():
        print(f"{nome} tentou acessar {tentativas} vezes.")
    
    print(f"\nQuantas invasões tivemos? {tentativasInvasao}")
    salvarRelatorio()
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, finalizar)

try:
    while True:
        print("Esperando...")
        tag, _ = leitorRfid.read()
        tag = str(tag)
        
        if tag in autorizacoes:
            nome = autorizacoes[tag]
            
            if tag not in tempoEntrada:
                tempoEntrada[tag] = [(time(), None)]
                print(f"Acesso autorizado, Olá {nome}")
                GPIO.output(ledVerde, GPIO.HIGH)
                tocarBuzzer(1000, 0.2)
                sleep(5)
                GPIO.output(ledVerde, GPIO.LOW)
            else:
                if tempoEntrada[tag][-1][1] is None:
                    tempoEntrada[tag][-1] = (tempoEntrada[tag][-1][0], time())
                    print(f"Até mais, {nome}")
                else:
                    tempoEntrada[tag].append((time(), None))
                    print(f"Acesso autorizado, Olá {nome}")
                
                GPIO.output(ledVerde, GPIO.HIGH)
                tocarBuzzer(1000, 0.2)
                sleep(5)
                GPIO.output(ledVerde, GPIO.LOW)
        
        elif tag in negacoes:
            nome = negacoes[tag]
            print(f"Acesso negado, você não tem acesso.")
            tentativasNegadas[nome] = tentativasNegadas.get(nome, 0) + 1
            GPIO.output(ledVermelho, GPIO.HIGH)
            tocarBuzzer(500, 0.5)
            sleep(5)
            GPIO.output(ledVermelho, GPIO.LOW)
        
        else:
            print("Identificação não encontrada")
            tentativasInvasao += 1
            tocarBuzzer(300, 1.0)
            for _ in range(10):
                GPIO.output(ledVermelho, GPIO.HIGH)
                sleep(0.5)
                GPIO.output(ledVermelho, GPIO.LOW)
                sleep(0.5)

finally:
    GPIO.cleanup()
