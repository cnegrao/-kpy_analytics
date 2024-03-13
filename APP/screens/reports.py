import streamlit as st
import pandas as pd
import duckdb
import locale

# Configuração do locale para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def load_indicators():
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        indicators = pd.read_sql_query("SELECT id, kpi_name FROM tb_kpi", conn)
    return indicators

def load_years(indicator_id):
    query = """
    SELECT DISTINCT year
    FROM tb_monthly_data
    WHERE kpi_id = ?
    ORDER BY year
    """
    indicator_id = int(indicator_id)
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        years = pd.read_sql_query(query, conn, params=(indicator_id,))
    return years['year'].tolist()

def load_monthly_data(indicator_id, year):
    query = """
    SELECT month, goal as Meta, value as Real
    FROM tb_monthly_data
    WHERE kpi_id = ? AND year = ?
    ORDER BY month
    """
    indicator_id = int(indicator_id)
    year = int(year)
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        monthly_data = pd.read_sql_query(query, conn, params=(indicator_id, year))
    monthly_data['month'] = monthly_data['month'].apply(lambda x: pd.to_datetime(f'{x}-01', format='%m-%d').strftime('%b'))
    return monthly_data

def calculate_desvio_and_farol(df):
    df['Desvio'] = ((df['Real'] - df['Meta']) / df['Meta']) * 100
    df['Farol Ícone'] = df.apply(lambda row: '🔵' if row['Real'] > row['Meta'] * 1.01 else
                                          '🟢' if row['Real'] >= row['Meta'] else
                                          '🟠' if row['Real'] >= row['Meta'] * 0.7 else
                                          '🔴', axis=1)
    # Renomeia as colunas para exibição
    df.rename(columns={'month': 'Mês', 'Farol Ícone': 'Farol'}, inplace=True)
    return df

def prepare_and_display_data(monthly_data):
     # Assegura que não estamos modificando o DataFrame original
    data = monthly_data.copy()

    # Renomeia as colunas conforme necessário
    data.rename(columns={'month': 'Mês', 'Farol Ícone': 'Farol'}, inplace=True)

    # Convertendo o DataFrame para uma lista de dicionários
    data_dicts = data.to_dict(orient='records')

    # Inicia a construção da tabela
    table_header = """| Mês | Real | Meta | Desvio | Farol |
| --- | --- | --- | --- | --- |"""
    table_rows = [table_header]

    for record in data_dicts:
        row = "| {Mês} | {Real} | {Meta} | {Desvio} | {Farol} |".format(**record)
        table_rows.append(row)

    # Combina todas as linhas em uma única string markdown e exibe
    table_markdown = "\n".join(table_rows)
    st.markdown(table_markdown, unsafe_allow_html=True)


    # Converter o DataFrame em uma lista de dicionários
    data_to_display = monthly_data.to_dict(orient='records')

    
   
def main():
    st.title("Relatórios de Desempenho")

    indicators_df = load_indicators()
    selected_indicator_name = st.selectbox('Selecione o indicador:', indicators_df['kpi_name'])

    if not indicators_df[indicators_df['kpi_name'] == selected_indicator_name].empty:
        selected_indicator_id = indicators_df[indicators_df['kpi_name'] == selected_indicator_name]['id'].iloc[0]

        years = load_years(selected_indicator_id)
        if years:
            selected_year = st.selectbox('Selecione o ano:', years)

            if selected_year:
                monthly_data = load_monthly_data(selected_indicator_id, selected_year)
                monthly_data = calculate_desvio_and_farol(monthly_data)
                st.write("Dados Mensais:")
                prepare_and_display_data(monthly_data)
                
    st.write("Legenda do Farol:")
    st.markdown("""
    - 🔵 Azul: Desempenho acima da meta (> 101% da meta)
    - 🟢 Verde: Desempenho na meta (≥ 100% da meta e ≤ 101% da meta)
    - 🟠 Laranja: Desempenho próximo da meta (≥ 70% da meta e < 100% da meta)
    - 🔴 Vermelho: Desempenho abaixo da meta (< 70% da meta)
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
