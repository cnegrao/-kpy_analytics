import streamlit as st
import pandas as pd
import duckdb
import locale

# Configuração do locale para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def load_indicators():
    """Carrega a lista de indicadores disponíveis no banco de dados."""
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        indicators = pd.read_sql_query("SELECT id, kpi_name FROM tb_kpi ORDER BY kpi_name", conn)
    return indicators

def load_years(indicator_id):
    """Carrega os anos disponíveis para o indicador selecionado."""
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        years = pd.read_sql_query(f"""
        SELECT DISTINCT year
        FROM tb_monthly_data
        WHERE kpi_id = {indicator_id}
        ORDER BY year""", conn)
    return years['year'].tolist()

def load_monthly_data(indicator_id, year):
    """Carrega os dados mensais do indicador e ano selecionados."""
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        monthly_data = pd.read_sql_query(f"""
        SELECT month, goal as Meta, value as Real
        FROM tb_monthly_data
        WHERE kpi_id = {indicator_id} AND year = {year}
        ORDER BY month ASC""", conn)
    monthly_data['month'] = monthly_data['month'].apply(lambda x: pd.to_datetime(f'{x}-01', format='%m-%d').strftime('%b'))
    return monthly_data

def calculate_indicators(df):
    """Calcula desvios e aplica o farol para dados mensais e acumulados, com tratamento para zeros."""
    df['Desvio'] = df.apply(lambda row: (row['Real'] - row['Meta']) / row['Meta'] * 100 if row['Meta'] > 0 else None, axis=1)
    df['Real Acumulado'] = df['Real'].cumsum()
    df['Meta Acumulada'] = df['Meta'].cumsum()
    df['Desvio Acumulado'] = df.apply(lambda row: (row['Real Acumulado'] - row['Meta Acumulada']) / row['Meta Acumulada'] * 100 if row['Meta Acumulada'] > 0 else None, axis=1)
    
    # Define os faróis baseados nas regras de desvio, tratando especificamente zeros em 'Real'
    def farol(value, real):
        if pd.isnull(value) or real == 0: return 'Sem dados'  # Trata casos sem dados ou com Real = 0
        elif value >= 110: return '🔵'
        elif value >= 100: return '🟢'
        elif value >= 85: return '🟠'
        else: return '🔴'

    df['Farol'] = df.apply(lambda row: farol(row['Desvio'], row['Real']), axis=1)
    df['Farol Acumulado'] = df.apply(lambda row: farol(row['Desvio Acumulado'], row['Real Acumulado']), axis=1)
    
    df.rename(columns={'month': 'Mês'}, inplace=True)
    return df


def prepare_and_display_data(data):
    """Prepara e exibe os dados calculados na interface do Streamlit."""
    st.write("Dados Mensais e Acumulados")
    st.dataframe(data[['Mês', 'Real', 'Meta', 'Desvio', 'Farol', 'Real Acumulado', 'Meta Acumulada', 'Desvio Acumulado', 'Farol Acumulado']], width=700, height=600)

def main():
    st.title("Relatórios de Desempenho")

    indicators_df = load_indicators()
    selected_indicator_id = st.selectbox('Selecione o indicador:', indicators_df['id'], format_func=lambda x: indicators_df[indicators_df['id'] == x]['kpi_name'].iloc[0])

    years = load_years(selected_indicator_id)
    if years:
        selected_year = st.selectbox('Selecione o ano:', years)

        monthly_data = load_monthly_data(selected_indicator_id, selected_year)
        indicators_data = calculate_indicators(monthly_data)
        prepare_and_display_data(indicators_data)

if __name__ == "__main__":
    main()
