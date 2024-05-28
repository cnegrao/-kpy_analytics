import streamlit as st
import pandas as pd
import duckdb
import locale
import plotly.graph_objects as go
import os
import datetime  # Importação do módulo datetime

# Configuração do locale para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para obter a conexão com o banco de dados


def get_db_connection():
    # Determina o caminho do banco de dados com base no ambiente
    if os.getenv('PRODUCTION'):
        # Caminho em ambiente de produção
        db_path = '/mount/src/-kpy_analytics/APP/data/kpi_analytics_db.duckdb'
    else:
        # Caminho local para desenvolvimento
        db_path = os.path.join(os.getcwd(), 'APP', 'data',
                               'kpi_analytics_db.duckdb')

    try:
        # Tenta conectar ao banco de dados e retorna a conexão
        connection = duckdb.connect(db_path)
        return connection
    except Exception as e:
        st.error(f"Failed to connect to the database at {db_path}. Error: {e}")
        raise

# Função para carregar os dados


def load_data(selected_year, selected_month):
    query = f"""
    SELECT 
        kpi.kpi_name AS Indicador,
        kpi.unity AS Unidade,
        kpi.direction AS Melhor,
        md.goal AS Meta,
        md.value AS Real,
        CASE
            WHEN md.value > md.goal * 1.01 THEN '🔵'
            WHEN md.value >= md.goal THEN '🟢'
            WHEN md.value >= md.goal * 0.70 THEN '🟡'
            ELSE '🔴'
        END AS Farol,
        SUM(md.goal) OVER (PARTITION BY md.kpi_id ORDER BY md.year, md.month) AS Meta_Acumulada,
        SUM(md.value) OVER (PARTITION BY md.kpi_id ORDER BY md.year, md.month) AS Real_Acumulado,
        CASE
            WHEN SUM(md.value) OVER (PARTITION BY md.kpi_id ORDER BY md.year, md.month) > SUM(md.goal) OVER (PARTITION BY md.kpi_id ORDER BY md.year, md.month) * 1.01 THEN '🔵'
            WHEN SUM(md.value) OVER (PARTITION BY md.kpi_id ORDER BY md.year, md.month) >= SUM(md.goal) OVER (PARTITION BY md.kpi_id ORDER BY md.year, md.month) THEN '🟢'
            WHEN SUM(md.value) OVER (PARTITION BY md.kpi_id ORDER BY md.year, md.month) >= SUM(md.goal) OVER (PARTITION BY md.kpi_id ORDER BY md.year, md.month) * 0.70 THEN '🟡'
            ELSE '🔴'
        END AS Farol_Acumulado,
        md.value - md.goal AS Absoluto,
        (md.value - md.goal) / NULLIF(md.goal, 0) * 100 AS Relativo
    FROM 
        tb_kpi kpi
    JOIN 
        tb_monthly_data md ON kpi.id = md.kpi_id
    WHERE 
        md.year = {selected_year} AND md.month = {selected_month}
    ORDER BY 
        kpi.id, md.year, md.month;
    """
    with get_db_connection() as conn:
        return pd.read_sql_query(query, conn)

# Função para exibir os dados em uma tabela no Streamlit


def display_data_table(df):
    # Formatação dos campos para exibição
    df['Meta'] = df['Meta'].apply(lambda x: f"{x:.2f}")
    df['Real'] = df['Real'].apply(lambda x: f"{x:.2f}")
    df['Meta_Acumulada'] = df['Meta_Acumulada'].apply(lambda x: f"{x:.2f}")
    df['Real_Acumulado'] = df['Real_Acumulado'].apply(lambda x: f"{x:.2f}")
    df['Absoluto'] = df['Absoluto'].apply(lambda x: f"{x:.2f}")
    df['Relativo'] = df['Relativo'].apply(lambda x: f"{x:.2f}%")

    # Criação da tabela Plotly
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color='navy',
            font=dict(color='white', size=12),
            align='left'
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color='lightgrey',
            font=dict(color='black', size=12),
            align='left'
        )
    )])

    # Ajustes finais de layout
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

    # Exibição da tabela no Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Função principal que roda a aplicação


def main():
    st.title("Relatório Agregado de Indicadores")

    # Filtros para ano e mês
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    selected_year = st.selectbox(
        'Selecione o Ano:', range(2022, current_year + 1), index=2)
    selected_month = st.selectbox(
        'Selecione o Mês:', range(1, 13), index=current_month - 1)

    # Carrega os dados do banco de dados
    df = load_data(selected_year, selected_month)

    # Exibe a tabela de dados
    display_data_table(df)


if __name__ == "__main__":
    main()
