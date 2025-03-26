import heapq

# =============================================================================
# Parâmetros do Gerador de Números Pseudoaleatórios (LCG)
# =============================================================================
# Parâmetros do LCG conforme visto em módulo:
a = 1664525
c = 1013904223
M = 2**32

# Variáveis globais do gerador (serão reiniciadas para cada simulação)
previous = 0
random_count = 0  # contador de números a serem usados na simulação

def reset_random(seed, count):
    """Reinicia o gerador com a semente e quantidade de números a gerar."""
    global previous, random_count
    previous = seed
    random_count = count

def next_random():
    """Gera o próximo número pseudoaleatório uniformizado entre 0 e 1."""
    global previous, random_count, a, c, M
    if random_count <= 0:
        raise Exception("Acabaram os números pseudoaleatórios!")
    random_count -= 1
    previous = (a * previous + c) % M
    return previous / M

# =============================================================================
# Função de Simulação da Fila
# =============================================================================
def simulate_queue(servers, capacity, first_arrival, min_arrival, max_arrival,
                   min_service, max_service, num_randoms, seed):
    """
    Simula uma fila com as seguintes características:
      • Chegada: Tempo uniforme entre min_arrival e max_arrival.
      • Serviço: Tempo uniforme entre min_service e max_service.
      • Capacidade máxima (incluindo atendimento e fila): capacity.
      • Número de servidores: servers.
      • Critério de parada: quando forem consumidos num_randoms números pseudoaleatórios.
    
    Retorna um dicionário com os resultados.
    """
    # Reiniciar gerador de números
    reset_random(seed, num_randoms)
    
    current_time = 0.0   # tempo corrente da simulação
    state = 0            # número de clientes no sistema (em atendimento e espera)
    losses = 0           # número de clientes perdidos (quando a fila está cheia)
    
    # Vetor de acúmulo de tempo para cada estado (0 até capacity)
    time_in_state = [0.0 for _ in range(capacity + 1)]
    
    # Lista de eventos (fila de prioridades): cada evento é (tempo, tipo)
    # Tipos de evento: "arrival" e "departure"
    event_list = []
    
    # Agendar a primeira chegada para first_arrival
    heapq.heappush(event_list, (first_arrival, "arrival"))
    
    # Loop principal de eventos
    while event_list and random_count > 0:
        event_time, event_type = heapq.heappop(event_list)
        
        # Acumula o tempo que o sistema passou no estado atual
        delta = event_time - current_time
        time_in_state[state] += delta
        current_time = event_time
        
        if event_type == "arrival":
            # Processa a chegada
            if state < capacity:
                state += 1  # cliente aceito
                # Se o número de clientes no sistema é menor ou igual que o número de servidores,
                # inicia imediatamente o atendimento deste cliente.
                if state <= servers:
                    try:
                        x = next_random()
                    except Exception:
                        break
                    service_time = min_service + (max_service - min_service) * x
                    departure_time = current_time + service_time
                    heapq.heappush(event_list, (departure_time, "departure"))
            else:
                # Fila cheia -> cliente perdido
                losses += 1
            
            # Agendar a próxima chegada
            try:
                x = next_random()
            except Exception:
                break
            interarrival = min_arrival + (max_arrival - min_arrival) * x
            next_arrival_time = current_time + interarrival
            heapq.heappush(event_list, (next_arrival_time, "arrival"))
        
        elif event_type == "departure":
            # Processa a saída do cliente (término do serviço)
            state -= 1
            # Se depois da saída o número de clientes no sistema for maior ou igual que 
            # o número de servidores, existe alguém aguardando e o atendimento do próximo
            # cliente deve ser iniciado imediatamente.
            if state >= servers:
                try:
                    x = next_random()
                except Exception:
                    break
                service_time = min_service + (max_service - min_service) * x
                departure_time = current_time + service_time
                heapq.heappush(event_list, (departure_time, "departure"))
    
    simulation_time = current_time  # tempo total da simulação
    
    # Calcula a probabilidade (em %) de cada estado com base no tempo acumulado
    probabilities = [ (t / simulation_time * 100) if simulation_time > 0 else 0
                      for t in time_in_state ]
    
    # Calcula a população média da fila:
    avg_population = sum(i * (time_in_state[i] / simulation_time)
                         for i in range(len(time_in_state))) if simulation_time > 0 else 0
    
    return {
        "simulation_time": simulation_time,
        "time_in_state": time_in_state,
        "probabilities": probabilities,
        "losses": losses,
        "avg_population": avg_population,
        "servers": servers,
        "capacity": capacity,
        "min_arrival": min_arrival,
        "max_arrival": max_arrival,
        "min_service": min_service,
        "max_service": max_service,
    }

# =============================================================================
# Função para Imprimir o Relatório da Simulação
# =============================================================================
def print_report(result, queue_label):
    print("=" * 60)
    print(f"Relatorio {queue_label}")
    print("=" * 60)
    print(f"Fila:   G/G/{result['servers']}/{result['capacity']}")
    print(f"Chegada: {result['min_arrival']} ... {result['max_arrival']}")
    print(f"Servico: {result['min_service']} ... {result['max_service']}")
    print("-" * 60)
    for i, (t, prob) in enumerate(zip(result["time_in_state"], result["probabilities"])):
        print(f"Estado {i:2d}: {t:11.4f} min  |  Probalidade: {prob:6.2f}%")
    print("Quantidade de perdas:", result["losses"])
    print("-" * 60)
    print(f"Tempo global de simulação: {result['simulation_time']:.4f} min")
    print(f"População média: {result['avg_population']:.4f}")
    print("=" * 60)
    print("\n")

# =============================================================================
# Execução da Simulação para as Duas Filas
# =============================================================================
if __name__ == "__main__":
    # Usaremos 100.000 números pseudoaleatórios conforme solicitado.
    NUM_RANDOMS = 100000
    SEED = 12345  # valor inicial da semente para o gerador
    
    # 1. Simulação da fila G/G/1/5:
    #    • 1 servidor, capacidade 5
    #    • Chegadas: tempo uniforme entre 2 e 5 minutos
    #    • Serviço: tempo uniforme entre 3 e 5 minutos
    #    • Primeira chegada em t = 2.0 minuto
    print("Simulação G/G/1/5:")
    result1 = simulate_queue(servers=1, capacity=5, first_arrival=2.0,
                             min_arrival=2.0, max_arrival=5.0,
                             min_service=3.0, max_service=5.0,
                             num_randoms=NUM_RANDOMS, seed=SEED)
    print_report(result1, "G/G/1/5")
    
    # 2. Simulação da fila G/G/2/5:
    #    • 2 servidores, capacidade 5
    #    • Chegadas: tempo uniforme entre 2 e 5 minutos
    #    • Serviço: tempo uniforme entre 3 e 5 minutos
    #    • Primeira chegada em t = 2.0 minuto
    print("Simulação G/G/2/5:")
    result2 = simulate_queue(servers=2, capacity=5, first_arrival=2.0,
                             min_arrival=2.0, max_arrival=5.0,
                             min_service=3.0, max_service=5.0,
                             num_randoms=NUM_RANDOMS, seed=SEED)
    print_report(result2, "G/G/2/5")
