#PESQUISA OPERACIONAL
#JOSÉ FLORÊNCIO E MARIA CLARA

import time
from pulp import (
    LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, LpStatus, value, PULP_CBC_CMD
)

# -------------------------------
# 1. DADOS REAIS DO ARTIGO
# -------------------------------

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

locais = clientes.copy()

# F_j = 0 (sem custo fixo)
F_j = {j: 0 for j in locais}

# C_ij: custo do cliente i para o centro j
C_ij = {}
for i in clientes:
    for j in locais:
        C_ij[(i, j)] = 0 if i == j else 9999

# custo do centro j para mercado k (ex.: km * custo_por_km)
dist_mercado = {'Europa_Mercosul': 150, 'Sudeste_BR': 2500}
custo_por_km = {'Europa_Mercosul': 0.13495, 'Sudeste_BR': 0.04211}

C_jk = {}
for j in locais:
    for k in mercados:
        C_jk[(j, k)] = custo_por_km[k] * dist_mercado[k]

M = 1e6

# -------------------------------
# 2. MODELO
# -------------------------------

modelo = LpProblem("Localizacao_CDs_Melao", LpMinimize)

X_ij = LpVariable.dicts("X", C_ij, lowBound=0)     # transporte cliente -> centro
Z_jk = LpVariable.dicts("Z", C_jk, lowBound=0)     # transporte centro -> mercado
Y_j = LpVariable.dicts("Y", locais, cat=LpBinary)  # abrir centro

# função objetivo
modelo += (
    lpSum(C_ij[i_j] * X_ij[i_j] for i_j in C_ij) +
    lpSum(C_jk[j_k] * Z_jk[j_k] for j_k in C_jk) +
    lpSum(F_j[j] * Y_j[j] for j in locais)
)

# restrições de produção (cada cliente i só pode fornecer até P_i[i])
for i in clientes:
    modelo += lpSum(X_ij[(i, j)] for j in locais if (i, j) in X_ij) <= P_i[i], f"ProdMax_{i}"

# atendimento de demanda nos mercados
for k in mercados:
    modelo += lpSum(Z_jk[(j, k)] for j in locais if (j, k) in Z_jk) >= D_k[k], f"Dem_{k}"

# ligação entrada/saída e ativação do centro (mantive a sua original)
for j in locais:
    entrada = lpSum(X_ij[(i, j)] for i in clientes if (i, j) in X_ij)
    saida = lpSum(Z_jk[(j, k)] for k in mercados if (j, k) in Z_jk)
    modelo += entrada + saida <= M * Y_j[j], f"Ativa_{j}"

# -------------- CORREÇÃO ESSENCIAL --------------
# Garantir conservação de fluxo: um centro não pode enviar mais do que recebeu
for j in locais:
    entrada = lpSum(X_ij[(i, j)] for i in clientes if (i, j) in X_ij)
    saida = lpSum(Z_jk[(j, k)] for k in mercados if (j, k) in Z_jk)
    modelo += saida <= entrada, f"ConservFlux_{j}"
# ------------------------------------------------

# -------------------------------
# 3. RESOLUÇÃO COM TEMPO
# -------------------------------

start_time = time.time()
modelo.solve(PULP_CBC_CMD(msg=0))
end_time = time.time()
elapsed_time = end_time - start_time

# -------------------------------
# 4. SAÍDA DETALHADA E CHECAGENS
# -------------------------------

tol = 1e-6  # tolerância para considerar fluxo > 0

print("\nResultado da Otimização")
print("------------------------")
print("Situação da solução encontrada:", "Ótima" if modelo.status == 1 else LpStatus[modelo.status])
print("Custo total obtido: R$", round(value(modelo.objective), 2))
print(f"Tempo de resolução: {elapsed_time:.4f} segundos")

# Listar CDs abertos e seu fluxo total (entrada+saida)
print("\nCentros de Distribuição (status e fluxos):")
abertos = []
for j in locais:
    yval = Y_j[j].varValue
    entrada = sum(X_ij[(i, j)].varValue or 0 for i in clientes if (i, j) in X_ij)
    saida = sum(Z_jk[(j, k)].varValue or 0 for k in mercados if (j, k) in Z_jk)
    total_fluxo = (entrada or 0) + (saida or 0)
    status = "ABERTO" if yval and yval > 0.5 else "FECHADO"
    print(f" - {j}: {status}; entrada={entrada:.1f} t; saída={saida:.1f} t; total={total_fluxo:.1f} t")
    if yval and yval > 0.5:
        abertos.append(j)

if not abertos:
    print(" - Nenhum centro foi marcado como aberto.")

# Transporte dos clientes até os centros (mostrar todos X_ij > tol)
print("\nTransporte dos clientes até os centros (X_ij):")
transporte_entrada = False
for (i, j), var in X_ij.items():
    qtd = var.varValue
    if qtd is not None and qtd > tol:
        print(f" - De {i} para {j}: {qtd:.2f} toneladas")
        transporte_entrada = True
if not transporte_entrada:
    print(" - Nenhum transporte registrado dos clientes até os centros.")

# Entregas dos centros aos mercados consumidores (Z_jk):"
print("\nEntregas dos centros aos mercados consumidores (Z_jk):")
transporte_saida = False
for (j, k), var in Z_jk.items():
    qtd = var.varValue
    if qtd is not None and qtd > tol:
        print(f" - De {j} para {k}: {qtd:.2f} toneladas")
        transporte_saida = True
if not transporte_saida:
    print(" - Nenhuma entrega registrada dos centros para os mercados.")

# -------------------------------
# 5. CHECAGENS DE CONSISTÊNCIA E CUSTO DETALHADO
# -------------------------------

total_produzido_alocado = sum((X_ij[(i, j)].varValue or 0) for (i, j) in X_ij)
total_enviado_mercados = sum((Z_jk[(j, k)].varValue or 0) for (j, k) in Z_jk)
total_demanda = sum(D_k.values())

print("\nChecagens:")
print(f" - Total demanda exigida: {total_demanda:.1f} t")
print(f" - Total enviado aos mercados (soma Z_jk): {total_enviado_mercados:.1f} t")
print(f" - Total produzido alocado (soma X_ij): {total_produzido_alocado:.1f} t")

print("\nAtendimento por mercado (soma por k):")
for k in mercados:
    atendido = sum((Z_jk[(j, k)].varValue or 0) for j in locais if (j, k) in Z_jk)
    print(f" - {k}: {atendido:.1f} / {D_k[k]:.1f} toneladas")

custo_entrada = sum(C_ij[i_j] * (X_ij[i_j].varValue or 0) for i_j in C_ij)
custo_saida = sum(C_jk[j_k] * (Z_jk[j_k].varValue or 0) for j_k in C_jk)
custo_fixo = sum(F_j[j] * (Y_j[j].varValue or 0) for j in locais)
custo_soma = custo_entrada + custo_saida + custo_fixo

print("\nQuebra de custo (checar consistência):")
print(f" - Custo transporte clientes->centros: R$ {custo_entrada:.2f}")
print(f" - Custo transporte centros->mercados: R$ {custo_saida:.2f}")
print(f" - Custo fixo abertura CDs: R$ {custo_fixo:.2f}")
print(f" - Soma parcial: R$ {custo_soma:.2f}")
print(f" - Objetivo reportado pelo solver: R$ {value(modelo.objective):.2f}")

if abs(custo_soma - value(modelo.objective)) > 1e-2:
    print("ATENÇÃO: soma dos componentes do custo difere do objetivo (possível problema numérico).")

print("\nRotas para mercados ordenadas por volume (maiores primeiro):")
rotas = []
for (j, k), var in Z_jk.items():
    qtd = var.varValue or 0
    if qtd > tol:
        rotas.append((qtd, j, k))
rotas.sort(reverse=True)
for qtd, j, k in rotas:
    custo_rot = C_jk[(j, k)] * qtd
    print(f" - {j} → {k}: {qtd:.2f} t (custo R$ {custo_rot:.2f})")

