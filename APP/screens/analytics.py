import streamlit as st
import duckdb
import pandas as pd

def main():
    st.title("Relatórios Acumulados")
    
    # Carregar os dados mensais
    df = load_monthly_data()
    
    # Ordenar os dados por ano e mês
    df_sorted = df.sort_values(by=['Ano', 'Mes'])
    
    # Calcular valores acumulados
    df_sorted['Valor_Acumulado'] = df_sorted.groupby('ID')['Real'].cumsum()
    
    # Calcular desvio acumulado
    df_sorted['Desvio_Acumulado'] = ((df_sorted['Valor_Acumulado'] - df_sorted['Meta'].cumsum()) / df_sorted['Meta'].cumsum()) * 100
    
    # Calcular farol acumulado
    df_sorted['Farol_Acumulado'] = df_sorted.apply(calculate_farol, axis=1)
    
    # Exibir a tabela na interface
    st.write("Dados Mensais Acumulados:")
    st.table(df_sorted[['AnoMes', 'Real', 'Meta', 'Valor_Acumulado', 'Desvio_Acumulado', 'Farol_Acumulado']])

def load_monthly_data():
    # Conectar ao banco de dados e executar a consulta
    conn = duckdb.connect("app/data/kpi_analytics_db.duckdb")
    df = pd.read_sql("""
        SELECT kpi_id as ID, "year" || LPAD(month, 2, '0') as AnoMes, value as Real, goal as Meta, "year" as Ano, month as Mes
        FROM tb_monthly_data
    """, conn)
    conn.close()
    return df

def calculate_farol(row):
    # Implemente o cálculo do farol acumulado (você pode usar a mesma lógica do cálculo do farol)
    real = row['Real']
    meta = row['Meta']
    if real > meta * 1.01:
        return 4
    elif real >= meta:
        return 3
    elif real >= meta * 0.7:
        return 2
    else:
        return 1

if __name__ == "__main__":
    main()
