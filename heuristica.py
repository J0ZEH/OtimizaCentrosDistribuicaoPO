import time

# ----------------------------------------
# INÍCIO DA CONTAGEM DE TEMPO
inicio = time.time()
# ----------------------------------------

# 1. Dados de entrada (mesmos que no modelo exato)
clientes = [
    'Aracati', 'Icapuí', 'Itaiçaba', 'Jaguaruana',
    'Limoeiro', 'Quixeré', 'Russas'
]

P_i = {
    'Aracati': 12000,
    'Icapuí': 6250,
    'Itaiçaba': 3875,
    'Jaguaruana': 2500,
    'Limoeiro': 2775,
    'Quixeré': 30500,
    'Russas': 50
}

mercados = ['Europa_Mercosul', 'Sudeste_BR']

D_k = {
    'Europa_Mercosul': 40565,
    'Sudeste_BR': 17385
}

# Distâncias médias (exemplo — ajustar se tiver dados reais)
dist_media = {
    'Aracati': 500,
    'Icapuí': 800,
    'Itaiçaba': 600,
    'Jaguaruana': 900,
    'Limoeiro': 750,
    'Quixeré': 700,
    'Russas': 1000
}

# Distância de cada CD para cada mercado
dist_mercado = {'Europa_Mercosul': 150, 'Sudeste_BR': 2500}

# Custo por km para cada mercado
custo_por_km = {'Europa_Mercosul': 0.13495, 'Sudeste_BR': 0.04211}

# ----------------------------------------
# 2. Cálculo do índice prioridade
prioridade = {}
for cidade in clientes:
    prioridade[cidade] = P_i[cidade] / dist_media[cidade]

# Ordena pela prioridade
ordenados = sorted(prioridade.keys(), key=lambda x: prioridade[x], reverse=True)

# ----------------------------------------
# 3. Seleção dos N CDs
N = 3  # alterar conforme necessário
CDs_abertos = ordenados[:N]

# Estoque inicial de cada CD
estoque_CD = {cd: P_i[cd] for cd in CDs_abertos}

# ----------------------------------------
# 4. Alocação das demandas
alocacao = []  # (CD, mercado, toneladas)
custo_total = 0

for mercado in mercados:
    demanda_restante = D_k[mercado]

    # CDs ordenados por distância até este mercado
    CDs_ordenados = sorted(CDs_abertos, key=lambda cd: dist_mercado[mercado])

    for cd in CDs_ordenados:
        if demanda_restante <= 0:
            break
        if estoque_CD[cd] > 0:
            quantidade = min(estoque_CD[cd], demanda_restante)
            estoque_CD[cd] -= quantidade
            demanda_restante -= quantidade
            custo_transporte = custo_por_km[mercado] * dist_mercado[mercado] * quantidade
            custo_total += custo_transporte
            alocacao.append((cd, mercado, quantidade))

# ----------------------------------------
# 5. Saída dos resultados
print("\nRESULTADO HEURÍSTICA")
print(f"CDs abertos: {CDs_abertos}")
print(f"Custo total: R$ {custo_total:,.2f}")
print("Alocação:")
for cd, mercado, qtd in alocacao:
    print(f" - {cd} → {mercado}: {qtd} toneladas")

# ----------------------------------------
# FIM DA CONTAGEM DE TEMPO
fim = time.time()
print(f"\nTempo de execução: {fim - inicio:.4f} segundos")
