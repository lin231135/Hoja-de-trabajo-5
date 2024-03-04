import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Semilla para la generación de números aleatorios
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

class Computadora:
    def __init__(self, env, ram, num_procesadores=1, instrucciones_por_tiempo=3):
        self.env = env
        self.cpu = simpy.Resource(env, capacity=num_procesadores)  # Procesadores
        self.ram = ram  # Memoria RAM
        self.instrucciones_por_tiempo = instrucciones_por_tiempo

    def correr_proceso(self, proceso):
        instrucciones_restantes = proceso['instrucciones_restantes']
        while instrucciones_restantes > 0:
            with self.cpu.request() as req:
                yield req
                yield self.env.timeout(1)  # Tiempo de ejecución de 1 unidad
                instrucciones_restantes -= self.instrucciones_por_tiempo  # Más instrucciones por tiempo
                proceso['instrucciones_restantes'] = instrucciones_restantes

                # Verificar si el proceso ha terminado
                if instrucciones_restantes <= 0:
                    proceso['estado'] = 'terminated'
                    break

                # Generar un número al azar para determinar el próximo estado
                random_num = random.randint(1, 21)
                if random_num == 1:
                    proceso['estado'] = 'waiting'
                    yield self.env.timeout(1)  # Tiempo de espera de 1 unidad
                    proceso['estado'] = 'ready'
                elif random_num == 2:
                    proceso['estado'] = 'ready'
                else:
                    continue

def llegada_proceso(env, computadora, tiempos_procesos, intervalo_llegada):
    id_proceso = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / intervalo_llegada))  # Intervalo de llegada de procesos
        id_proceso += 1
        instrucciones_totales = random.randint(1, 10)  # Número de instrucciones totales para el proceso
        memoria_requerida = random.randint(1, 10)  # Cantidad de memoria RAM requerida por el proceso
        proceso = {'id': id_proceso, 'instrucciones_restantes': instrucciones_totales, 'estado': 'new'}

        # Solicitar memoria RAM para el proceso
        yield computadora.ram.get(memoria_requerida)

        # Pasar al estado de 'ready' si hay suficiente memoria RAM disponible
        proceso['estado'] = 'ready'
        env.process(computadora.correr_proceso(proceso))

        # Devolver memoria RAM al finalizar el proceso
        yield env.timeout(1)  # Tiempo simulado de 1 unidad para la ejecución
        yield computadora.ram.put(memoria_requerida)

        # Almacenar tiempo de proceso para la gráfica
        tiempos_procesos.append(env.now)

# Función para ejecutar la simulación con diferentes configuraciones
def ejecutar_simulacion(num_procesos, intervalo_llegada, ram_capacity=100, num_procesadores=1, instr_por_tiempo=3):
    env = simpy.Environment()
    ram = simpy.Container(env, init=ram_capacity, capacity=ram_capacity)  # Memoria RAM
    computadora = Computadora(env, ram, num_procesadores, instr_por_tiempo)
    tiempos_procesos = []
    env.process(llegada_proceso(env, computadora, tiempos_procesos, intervalo_llegada))
    env.run(until=num_procesos)

    # Calcular el tiempo promedio de proceso
    if tiempos_procesos:
        tiempo_promedio = np.mean(tiempos_procesos)
    else:
        tiempo_promedio = 0

    return tiempo_promedio

# Realizar simulaciones y graficar resultados para cada cambio
def realizar_simulaciones():
    configuraciones = [
        {'ram_capacity': 200, 'num_procesadores': 1, 'instr_por_tiempo': 3},
        {'ram_capacity': 100, 'num_procesadores': 1, 'instr_por_tiempo': 6},
        {'ram_capacity': 100, 'num_procesadores': 2, 'instr_por_tiempo': 3}
    ]
    intervalos_llegada = [10, 5, 1]
    num_procesos_lista = [25, 50, 100, 150, 200]

    for config in configuraciones:
        tiempos_promedio_dict = {}
        for intervalo in intervalos_llegada:
            tiempos_promedio = []
            for num_procesos in num_procesos_lista:
                tiempo_promedio = ejecutar_simulacion(num_procesos, intervalo, **config)
                tiempos_promedio.append(tiempo_promedio)
            tiempos_promedio_dict[intervalo] = tiempos_promedio

        # Graficar resultados para cada configuración
        plt.figure(figsize=(10, 6))
        for intervalo, tiempos_promedio in tiempos_promedio_dict.items():
            plt.plot(num_procesos_lista, tiempos_promedio, marker='o', label=f'Intervalo de llegada: {intervalo}')
        plt.xlabel('Número de Procesos')
        plt.ylabel('Tiempo Promedio de Proceso')
        plt.title('Tiempo Promedio de Proceso vs Número de Procesos')
        plt.legend()
        plt.grid(True)
        plt.show()

# Ejecutar simulaciones
realizar_simulaciones()