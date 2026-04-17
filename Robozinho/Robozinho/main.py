#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import ColorSensor, Motor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# Inicializa os Motores

motor_esquerdo = Motor(Port.A)
motor_direito = Motor(Port.D)

# Inicializa o sensor de Cor.

sensor_c = ColorSensor(Port.S2)
sensor_d = UltrasonicSensor(Port.S4)
# Inicializa o Objeto Drive Base, que controla os motores de forma paralela.

robo = DriveBase(motor_esquerdo, motor_direito, wheel_diameter=55.5, axle_track=127)

# Calcule o limiar de luz.

preto = 8 # 6 Chão
branco = 28 # 36 chão
limiar = (preto + branco) / 2 # Pega a media

# Define a velocidade do robo a um valor x milimetros por segundo.
velocidade = 120

# Define o ganho do controlador de linha proporcional.
# Isso significa que para cada ponto percentual de luz fora do limite
# definimos a curva

# taxa de gango proporcional de curva para 4,7 graus por segundo.

# Se o valor da luz se desviar do limite em 10, o robô
# dirige a 10*4,7 = 47 graus por segundo.

ganho_proporcional = 4.7 # 4,7 cor do Chão

# Loop para seguir a linha sem ponto de parada.

def desviar_obstaculo():
    robo.stop()
    wait(200)

    # 1️⃣ Vira DIREITA — rápido
    robo.drive(0, -200)
    wait(500)

    # 2️⃣ Anda reto — passa pelo obstáculo
    robo.drive(velocidade, 0)
    wait(1000)

    # 3️⃣ Vira ESQUERDA — rápido
    robo.drive(0, 200)
    wait(500)

    # 4️⃣ Anda reto — avança além do obstáculo
    robo.drive(velocidade, 0)
    wait(1000)

    # 5️⃣ Vira ESQUERDA — rápido
    robo.drive(0, 200)
    wait(500)

    # 6️⃣ Vira ESQUERDA — bem devagar pra sentir a linha
    while True:
        robo.drive(40, 0)  # reto, bem devagar
        cor = sensor_c.reflection()
        if cor < limiar:
            robo.stop()
            break
        wait(10)

     # 7️⃣ Realinha — vira pra DIREITA pra ficar paralelo à linha
    robo.drive(0, -90)
    wait(200)
    robo.stop()
       
        
while True:

    distancia = sensor_d.distance()
    print(distancia)
    if distancia <= 50: 
        desviar_obstaculo()
        continue
    
    # Calcula o desvio do limite.
    cor_lida = sensor_c.reflection()

    desvio = cor_lida - limiar

    # Calcula a taxa de rotação

    taxa_de_rot = ganho_proporcional * desvio

    # Define a velocidade base e a taxa de rotação

    robo.drive(velocidade, taxa_de_rot)

    wait(10)

    # Cor da linha de Chegada, se chegar ele vai andar por 3 segundos antes de parar

    if cor_lida > 48:

        robo.drive(velocidade,0)
        wait(3000)
        robo.stop()
        break

    # Para que o Robô não fique constantemente alterando os valores e se perdendo é adicionada 10 ms de intervalo
