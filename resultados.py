import matplotlib.pyplot as plt

# Dados
metodos = ['Modelo Exato', 'Heurística']
custos = [2651342.89, 1682812.89]
tempos = [0.709, 0.001]  # em segundos

# 1. Gráfico de Custo Total
plt.figure(figsize=(6,4))
plt.bar(metodos, custos, color=['steelblue', 'orange'])
plt.ylabel('Custo Total (R$)')
plt.title('Comparação de Custo Total')
for i, v in enumerate(custos):
    plt.text(i, v + 50000, f'R$ {v:,.2f}', ha='center')
plt.tight_layout()
plt.savefig('comparacao_custos.png', dpi=300)
plt.show()

# 2. Gráfico de Tempo de Execução
plt.figure(figsize=(6,4))
plt.bar(metodos, tempos, color=['steelblue', 'orange'])
plt.ylabel('Tempo (segundos)')
plt.title('Comparação de Tempo de Execução')
for i, v in enumerate(tempos):
    plt.text(i, v + 0.01, f'{v:.3f}s', ha='center')
plt.tight_layout()
plt.savefig('comparacao_tempos.png', dpi=300)
plt.show()
