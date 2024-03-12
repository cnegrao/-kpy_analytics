import streamlit as st
import pandas as pd
import duckdb

def main():
    st.title("Análise Acumulada")

    # Carregar os dados mensais
    df = load_monthly_data()

    # Adicionar filtro para selecionar o ano
    years = sorted(df['Ano'].unique(), reverse=True)
    selected_year = st.selectbox('Selecione o ano:', years)

    # Filtrar os dados pelo ano selecionado
    df_filtered = df[df['Ano'] == selected_year]

    # Calcular os valores acumulados
    df_filtered['Valor_Acumulado'] = df_filtered.groupby('ID')['Real'].cumsum()
    df_filtered['Meta_Acumulada'] = df_filtered.groupby('ID')['Meta'].cumsum()
    df_filtered['Desvio_Acumulado'] = ((df_filtered['Valor_Acumulado'] / df_filtered['Meta_Acumulada']) - 1) * 100
    df_filtered['Farol_Acumulado'] = df_filtered.apply(calculate_farol, axis=1)

    # Exibir a tabela na interface
    st.write("Dados Acumulados para o ano de", selected_year)
    st.table(df_filtered[['AnoMes', 'Real', 'Meta', 'Desvio_Acumulado', 'Farol_Acumulado']])

def load_monthly_data():
    # Conectar ao banco de dados para carregar os dados mensais
    conn = duckdb.connect("app/data/kpi_analytics_db.duckdb")

    # Executar a consulta SQL para carregar os dados
    df = pd.read_sql("""
        SELECT kpi_id as ID, "year" || '-' || CASE WHEN month < 10 THEN '0' || CAST(month AS VARCHAR) ELSE CAST(month AS VARCHAR) END as AnoMes, value as Real, goal as Meta, "year" as Ano, month as Mes
        FROM tb_monthly_data
    """, conn)

    # Fechar a conexão com o banco de dados
    conn.close()

    return df

def calculate_farol(row):
    # Calcular o farol com base no valor real e na meta
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
