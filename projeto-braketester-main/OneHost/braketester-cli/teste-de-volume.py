import subprocess
import time

def executar_programa_n_vezes(programa, argumento, n):
    tempo_inicial = time.time()
    n_incremento = 0
    while True:
        for _ in range(n):
            n_incremento += 1
            concatenada = " ".join([argumento, str(n_incremento)])
            subprocess.run(['python3', programa, concatenada])
        break

# Exemplo de uso
programa = 'register-braketest.py'  # Substitua pelo caminho para o programa que você deseja executar
argumento = 'AAA0000'  # Substitua pela string que você deseja passar como argumento
n_vezes = 60  # Número de vezes que o programa será executado
executar_programa_n_vezes(programa, argumento, n_vezes)

