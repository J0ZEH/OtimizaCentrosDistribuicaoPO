import time
from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, LpStatus, value
from pulp import PULP_CBC_CMD

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

F_j = {j: 0 for j in locais}  # Sem custo fixo no estudo

C_ij = {}
for i in clientes:
    for j in locais:
        C_ij[(i, j)] = 0 if i == j else 9999  # Apenas CDs locais

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

X_ij = LpVariable.dicts("X", C_ij, lowBound=0)
Z_jk = LpVariable.dicts("Z", C_jk, lowBound=0)
Y_j = LpVariable.dicts("Y", locais, cat=LpBinary)

modelo += (
    lpSum(C_ij[i_j] * X_ij[i_j] for i_j in C_ij) +
    lpSum(C_jk[j_k] * Z_jk[j_k] for j_k in C_jk) +
    lpSum(F_j[j] * Y_j[j] for j in locais)
)

for i in clientes:
    modelo += lpSum(X_ij[(i, j)] for j in locais if (i, j) in X_ij) <= P_i[i]

for k in mercados:
    modelo += lpSum(Z_jk[(j, k)] for j in locais if (j, k) in Z_jk) >= D_k[k]

for j in locais:
    entrada = lpSum(X_ij[(i, j)] for i in clientes if (i, j) in X_ij)
    saida = lpSum(Z_jk[(j, k)] for k in mercados if (j, k) in Z_jk)
    modelo += entrada + saida <= M * Y_j[j]

# -------------------------------
# 3. RESOLUÇÃO COM TEMPO
# -------------------------------

start_time = time.time()  # Marca o início

modelo.solve(PULP_CBC_CMD(msg=0))

end_time = time.time()  # Marca o fim

elapsed_time = end_time - start_time  # Tempo decorrido em segundos

# -------------------------------
# 4. SAÍDA
# -------------------------------

print("\nResultado da Otimização")
print("------------------------")

print("Situação da solução encontrada:", "Ótima" if modelo.status == 1 else LpStatus[modelo.status])
print("Custo total obtido: R$", round(value(modelo.objective), 2))
print(f"Tempo de resolução: {elapsed_time:.4f} segundos")

print("\nCentros de Distribuição abertos:")
for j in locais:
    if Y_j[j].varValue > 0.5:
        print(f" - {j}")

print("\nTransporte dos clientes até os centros:")
transporte_entrada = False
for (i, j), var in X_ij.items():
    if var.varValue and var.varValue > 0:
        print(f" - De {i} para {j}: {var.varValue:.1f} toneladas")
        transporte_entrada = True
if not transporte_entrada:
    print(" - Nenhum transporte registrado dos clientes até os centros.")

print("\nEntregas dos centros aos mercados consumidores:")
transporte_saida = False
for (j, k), var in Z_jk.items():
    if var.varValue and var.varValue > 0:
        print(f" - De {j} para {k}: {var.varValue:.1f} toneladas")
        transporte_saida = True
if not transporte_saida:
    print(" - Nenhuma entrega registrada dos centros para os mercados.")
