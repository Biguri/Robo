#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait

class LineFollower:
    def __init__(self):
        self.ev3 = EV3Brick()
        self.motor_esq = Motor(Port.D, Direction.CLOCKWISE)
        self.motor_dir = Motor(Port.A, Direction.CLOCKWISE)
        self.sensor = ColorSensor(Port.S2)

        # Parâmetros PD
        self.velocidade_base = 50
        self.kp = 0.8   # Ganho proporcional
        self.kd = 1.2   # Ganho derivativo (reduz oscilação)

    def _wait_button_press_release(self):
        """Aguarda apertar E soltar o botão central — evita detecção dupla."""
        while Button.CENTER not in self.ev3.buttons.pressed():
            wait(50)
        while Button.CENTER in self.ev3.buttons.pressed():
            wait(50)

    def _stop_motors(self):
        """Para ambos os motores com freio."""
        self.motor_esq.stop(Stop.BRAKE)
        self.motor_dir.stop(Stop.BRAKE)

    def calibrate_sensor(self):
        """Calibra os valores de reflexão para PRETO e BRANCO."""
        self.ev3.screen.clear()
        self.ev3.screen.print("=== CALIBRACAO ===")

        # --- Preto ---
        self.ev3.screen.print("Sensor sobre PRETO")
        self.ev3.screen.print("Pressione CENTER")
        self._wait_button_press_release()
        wait(300)

        valor_preto = self.sensor.reflection()
        self.ev3.screen.print("PRETO: " + str(valor_preto))
        wait(800)

        # --- Branco ---
        self.ev3.screen.print("Sensor sobre BRANCO")
        self.ev3.screen.print("Pressione CENTER")
        self._wait_button_press_release()
        wait(300)

        valor_branco = self.sensor.reflection()
        self.ev3.screen.print("BRANCO: " + str(valor_branco))
        wait(800)

        # Valida calibração
        if abs(valor_branco - valor_preto) < 10:
            self.ev3.screen.print("AVISO: diferenca")
            self.ev3.screen.print("muito pequena!")
            self.ev3.light.on(Color.RED)
            wait(2000)
        else:
            self.ev3.light.on(Color.GREEN)

        target = (valor_preto + valor_branco) / 2
        self.ev3.screen.print("BORDA: " + str(int(target)))
        wait(1000)

        return valor_preto, valor_branco, target

    def test_motor_simple(self):
        """Testa cada motor individualmente e depois os dois juntos."""
        self.ev3.screen.clear()
        self.ev3.screen.print("=== TESTE MOTORES ===")

        testes = [
            ("ESQ frente", self.motor_esq, None, 80),
            ("ESQ tras",   self.motor_esq, None, -80),
            ("DIR frente", None, self.motor_dir, 80),
            ("DIR tras",   None, self.motor_dir, -80),
            ("AMBOS",      self.motor_esq, self.motor_dir, 80),
        ]

        for nome, m_e, m_d, vel in testes:
            self.ev3.screen.clear()
            self.ev3.screen.print(nome)
            if m_e: m_e.run(vel)
            if m_d: m_d.run(vel)
            wait(1500)
            self._stop_motors()
            wait(400)

        self.ev3.screen.print("Teste OK!")

    def follow_line_with_calibration(self, target):
        """Segue a linha usando controle PD."""
        self.ev3.screen.clear()
        self.ev3.screen.print("=== SEGUIR LINHA ===")
        self.ev3.screen.print("Posicione na borda")
        self.ev3.screen.print("CENTER para iniciar")
        self._wait_button_press_release()
        wait(300)

        self.ev3.screen.clear()
        self.ev3.screen.print("Rodando...")
        self.ev3.screen.print("CENTER para parar")
        self.ev3.light.on(Color.GREEN)

        erro_anterior = 0
        contador_print = 0  # Imprime a cada N ciclos, não sempre

        try:
            while Button.CENTER not in self.ev3.buttons.pressed():
                sensor_value = self.sensor.reflection()

                # Controle PD
                erro = target - sensor_value
                derivativo = erro - erro_anterior
                correcao = (self.kp * erro) + (self.kd * derivativo)
                erro_anterior = erro

                # Limita correção
                correcao = max(min(correcao, 30), -30)

                pot_esq = int(self.velocidade_base - correcao)
                pot_dir = int(self.velocidade_base + correcao)

                # Limita velocidade de cada motor
                pot_esq = max(-100, min(100, pot_esq))
                pot_dir = max(-100, min(100, pot_dir))

                self.motor_esq.run(pot_esq)
                self.motor_dir.run(pot_dir)

                # Print reduzido: só a cada 10 ciclos
                contador_print += 1
                if contador_print >= 10:
                    self.ev3.screen.clear()
                    self.ev3.screen.print("S:" + str(sensor_value))
                    self.ev3.screen.print("E:" + str(pot_esq))
                    self.ev3.screen.print("D:" + str(pot_dir))
                    contador_print = 0

                wait(20)  # Loop mais rápido (era 100ms)

        finally:
            # Garante parada mesmo se ocorrer exceção
            self._stop_motors()
            self.ev3.light.off()
            self.ev3.screen.clear()
            self.ev3.screen.print("Parado!")

    def run(self):
        """Menu principal com seleção de modo."""
        self.ev3.screen.clear()
        self.ev3.screen.print("=== LINE FOLLOWER ===")
        self.ev3.screen.print("UP   = Testar motores")
        self.ev3.screen.print("DOWN = Seguir linha")
        self.ev3.screen.print("Aguardando...")

        # Aguarda botão UP ou DOWN — corrigido para usar Button enum
        while True:
            pressed = self.ev3.buttons.pressed()
            if Button.UP in pressed:
                # Espera soltar
                while Button.UP in self.ev3.buttons.pressed():
                    wait(50)
                self.test_motor_simple()
                break
            elif Button.DOWN in pressed:
                while Button.DOWN in self.ev3.buttons.pressed():
                    wait(50)
                _, _, target = self.calibrate_sensor()
                self.follow_line_with_calibration(target)
                break
            wait(50)

if __name__ == "__main__":
    robot = LineFollower()
    robot.run()