import streamlit as st
import duckdb
import pandas as pd

def main():
    st.title("Relatórios")
    
    # Carregar os indicadores para preencher o dropdown
    indicators = load_indicators()
    selected_indicator_name = st.selectbox('Selecione o indicador:', [indicator[1] for indicator in indicators])

    # Carregar os anos disponíveis para o indicador selecionado
    years = load_years(selected_indicator_name)
    selected_year = st.selectbox('Selecione o ano:', years)

    # Carregar os dados mensais para o indicador e o ano selecionados
    monthly_data = load_monthly_data(selected_indicator_name, selected_year)

    # Converter os dados para DataFrame do Pandas
    df = pd.DataFrame(monthly_data, columns=['Meta', 'Real', 'Ano', 'Mes'])

    # Concatenar ano e mês para formar a coluna AnoMes
    df['AnoMes'] = df['Ano'].astype(str) + df['Mes'].astype(str).str.zfill(2)

    # Calcular o desvio e o farol para cada mês
    df['Desvio'] = df.apply(calculate_desvio, axis=1)
    df['Farol'] = df.apply(calculate_farol, axis=1)

    # Exibir a tabela na interface
    st.write("Dados Mensais:")
    st.table(df[['AnoMes', 'Real', 'Meta', 'Desvio', 'Farol']])

def load_indicators():
    # Conectar ao banco de dados para carregar os indicadores
    conn = duckdb.connect("app/data/kpi_analytics_db.duckdb")
    indicators = conn.execute("SELECT id, kpi_name FROM tb_kpi").fetchall()
    conn.close()
    return indicators

def load_years(selected_indicator_name):
    # Conectar ao banco de dados para carregar os anos disponíveis para o indicador selecionado
    conn = duckdb.connect("app/data/kpi_analytics_db.duckdb")
    years = conn.execute("""
        SELECT DISTINCT "year"
        FROM tb_monthly_data
        WHERE kpi_id = (SELECT id FROM tb_kpi WHERE kpi_name = ?)
    """, (selected_indicator_name,)).fetchall()
    conn.close()
    return [year[0] for year in years]

def load_monthly_data(selected_indicator_name, selected_year):
    # Conectar ao banco de dados para carregar os dados mensais para o indicador e o ano selecionados
    conn = duckdb.connect("app/data/kpi_analytics_db.duckdb")
    monthly_data = conn.execute("""
        SELECT goal as Meta, value as Real, "year" as Ano, month as Mes
        FROM tb_monthly_data
        WHERE kpi_id = (SELECT id FROM tb_kpi WHERE kpi_name = ?)
        AND "year" = ?
    """, (selected_indicator_name, selected_year)).fetchall()
    conn.close()
    return monthly_data

def calculate_desvio(row):
    # Calcular o desvio em percentual
    real = row['Real']
    meta = row['Meta']
    if meta != 0:
        return ((real - meta) / meta) * 100
    else:
        return 0

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
