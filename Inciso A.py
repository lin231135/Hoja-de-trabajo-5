import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Semilla para la generación de números aleatorios
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

class Computadora:
    def __init__(self, env, ram):
        self.env = env
        self.cpu = simpy.Resource(env, capacity=1)  # CPU
        self.ram = ram  # Memoria RAM

    def correr_proceso(self, proceso):
        instrucciones_restantes = proceso['instrucciones_restantes']
        while instrucciones_restantes > 0:
            with self.cpu.request() as req:
                yield req
                yield self.env.timeout(1)  # Tiempo de ejecución de 1 unidad (equivalente a una instrucción)
                instrucciones_restantes -= 3  # Se ejecutan 3 instrucciones en cada ciclo de CPU
                proceso['instrucciones_restantes'] = instrucciones_restantes

                # Verificar si el proceso ha terminado
                if instrucciones_restantes <= 0:
                    proceso['estado'] = 'terminated'
                    print(f"Proceso {proceso['id']} terminado en {self.env.now}")
                    break

                # Generar un número al azar para determinar el próximo estado
                random_num = random.randint(1, 21)
                if random_num == 1:
                    proceso['estado'] = 'waiting'
                    print(f"Proceso {proceso['id']} en estado de espera en {self.env.now}")
                    yield self.env.timeout(1)  # Tiempo de espera de 1 unidad
                    proceso['estado'] = 'ready'
                    print(f"Proceso {proceso['id']} listo para correr nuevamente en {self.env.now}")
                elif random_num == 2:
                    proceso['estado'] = 'ready'
                    print(f"Proceso {proceso['id']} listo para correr nuevamente en {self.env.now}")
                else:
                    continue

def llegada_proceso(env, computadora, tiempos_procesos):
    id_proceso = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / 10))  # Intervalo de llegada de procesos exponencial con tasa 10
        id_proceso += 1
        instrucciones_totales = random.randint(1, 10)  # Número de instrucciones totales para el proceso
        memoria_requerida = random.randint(1, 10)  # Cantidad de memoria RAM requerida por el proceso
        proceso = {'id': id_proceso, 'instrucciones_restantes': instrucciones_totales, 'estado': 'new'}

        # Solicitar memoria RAM para el proceso
        yield computadora.ram.get(memoria_requerida)
        print(f"Proceso {id_proceso} obtiene memoria RAM en {env.now}")

        # Pasar al estado de 'ready' si hay suficiente memoria RAM disponible
        proceso['estado'] = 'ready'
        env.process(computadora.correr_proceso(proceso))

        # Devolver memoria RAM al finalizar el proceso
        yield env.timeout(1)  # Tiempo simulado de 1 unidad para la ejecución
        yield computadora.ram.put(memoria_requerida)
        print(f"Proceso {id_proceso} libera memoria RAM en {env.now}")

        # Almacenar tiempo de proceso para la grafica
        tiempos_procesos.append(env.now)

def ejecutar_simulacion(num_procesos):
    env = simpy.Environment()
    ram = simpy.Container(env, init=100, capacity=100)  # Memoria RAM
    computadora = Computadora(env, ram)
    tiempos_procesos = []
    env.process(llegada_proceso(env, computadora, tiempos_procesos))
    env.run(until=num_procesos)

    # Calcular el tiempo promedio de proceso
    if tiempos_procesos:
        tiempo_promedio = np.mean(tiempos_procesos)
        desviacion_estandar = np.std(tiempos_procesos)
    else:
        tiempo_promedio = 0
        desviacion_estandar = 0

    return tiempo_promedio, desviacion_estandar

# Ejecutar simulación y graficar
num_procesos_lista = [25, 50, 100, 150, 200]
tiempos_promedio = []
desviaciones_estandar = []

for num_procesos in num_procesos_lista:
    tiempo_promedio, desviacion_estandar = ejecutar_simulacion(num_procesos)
    tiempos_promedio.append(tiempo_promedio)
    desviaciones_estandar.append(desviacion_estandar)

    print(f"Número de Procesos: {num_procesos}, Tiempo Promedio: {tiempo_promedio}, Desviación Estándar: {desviacion_estandar}")

# Graficar
plt.errorbar(num_procesos_lista, tiempos_promedio, yerr=desviaciones_estandar, fmt='o-', capsize=5)
plt.xlabel('Número de Procesos')
plt.ylabel('Tiempo Promedio de Proceso')
plt.title('Tiempo Promedio de Proceso vs Número de Procesos')
plt.grid(True)
plt.show()
