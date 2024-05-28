import duckdb
import pandas as pd
from random import uniform

# Conectar ao banco de dados DuckDB
conn = duckdb.connect(
    database='D:\\#kpy_analytics\\APP\\data\\kpi_analytics_db.duckdb')

# Lista de KPIs a serem excluídos
exclude_kpis = [1, 5, 19, 2]

# Gerar dados para os outros KPIs
data = []
for kpi_id in range(1, 40):
    if kpi_id not in exclude_kpis:
        for year in [2024, 2025]:
            for month in range(1, 13 if year == 2024 else 6):
                goal = round(uniform(1, 100), 2)
                value = round(uniform(1, 100), 2)
                data.append((kpi_id, year, month, goal, value))

# Criar um DataFrame
df = pd.DataFrame(data, columns=['kpi_id', 'year', 'month', 'goal', 'value'])

# Inserir os dados no banco de dados
conn.executemany('''
INSERT INTO tb_monthly_data (kpi_id, year, month, goal, value) VALUES (?, ?, ?, ?, ?)
''', data)

# Verificar os dados
result = conn.execute('SELECT * FROM tb_monthly_data').fetchall()
result_df = pd.DataFrame(
    result, columns=['kpi_id', 'year', 'month', 'goal', 'value'])
print(result_df)
