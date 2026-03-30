#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# Objetos
robo = EV3Brick()
sensor_cor = ColorSensor(Port.S4)
sensor_ultra = UltrasonicSensor(Port.S1)

# Motores nas portas A e B
motor_esq = Motor(Port.A, Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.B, Direction.COUNTERCLOCKWISE)

# DriveBase
drive = DriveBase(
    motor_esq,
    motor_dir,
    wheel_diameter=56,
    axle_track=120  # mm — meça e ajuste!
)

# Velocidade compensada para relação 1:4
drive.settings(
    straight_speed=600,
    straight_acceleration=200,
    turn_rate=90,
    turn_acceleration=60
)

DISTANCIA_PARADA = 15  # cm

robo.screen.clear()
robo.screen.print("Andando!")

while True:
    distancia = sensor_ultra.distance() / 10  # mm para cm

    # Obstáculo detectado — para imediatamente
    if distancia < DISTANCIA_PARADA:
        drive.stop()
        robo.screen.clear()
        robo.screen.print("OBSTACULO!")
        robo.screen.print(str(distancia) + " cm")
        wait(200)

    # Sem obstáculo — anda reto independente de cor
    else:
        robo.screen.clear()
        robo.screen.print("Andando!")
        robo.screen.print(str(distancia) + " cm")
        drive.drive(150, 0)  # 150mm/s, 0 = reto

    wait(100)