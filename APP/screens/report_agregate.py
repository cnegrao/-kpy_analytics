import os
import streamlit as st
import pandas as pd
import duckdb
import locale
import plotly.graph_objects as go
import datetime

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

# Função para carregar os dados para uma categoria específica


def load_data_for_category(selected_year, selected_month, category_id):
    query = f"""
    SELECT 
        kpi.kpi_name AS Indicador,
        kpi.unity AS Unidade,
        CASE 
            WHEN kpi.direction = 'up' THEN '⬆️'
            WHEN kpi.direction = 'down' THEN '⬇️'
            ELSE kpi.direction
        END AS Melhor,
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
        kpi.idKpiCategory = {category_id} AND md.year = {selected_year} AND md.month <= {selected_month}
    ORDER BY 
        kpi.id, md.year, md.month;
    """
    with get_db_connection() as conn:
        return pd.read_sql_query(query, conn)

# Função para exibir os dados em uma tabela no Streamlit


def display_data_table(df):
    # Formatação dos campos para exibição
    df['Meta'] = df['Meta'].apply(lambda x: f"{x * 100:.2f}%")
    df['Real'] = df['Real'].apply(lambda x: f"{x * 100:.2f}%")
    df['Meta_Acumulada'] = df['Meta_Acumulada'].apply(
        lambda x: f"{x * 100:.2f}%")
    df['Real_Acumulado'] = df['Real_Acumulado'].apply(
        lambda x: f"{x * 100:.2f}%")
    df['Absoluto'] = df['Absoluto'].apply(lambda x: f"{x:.2f}")
    df['Relativo'] = df['Relativo'].apply(lambda x: f"{x:.2f}%")

    # Renomear colunas
    df.rename(columns={
        'Meta_Acumulada': 'Meta Acumulada (%)',
        'Real_Acumulado': 'Real Acumulado (%)'
    }, inplace=True)

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

# Função para criar gráficos acumulados


def create_accumulated_chart(df, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Indicador'],
        y=df['Meta_Acumulada'].apply(lambda x: float(x.strip('%'))),
        mode='lines+markers',
        name='Meta Acumulada',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df['Indicador'],
        y=df['Real_Acumulado'].apply(lambda x: float(x.strip('%'))),
        mode='lines+markers',
        name='Real Acumulado',
        line=dict(color='red', width=2)
    ))
    fig.update_layout(
        title=title,
        xaxis_title='Indicadores',
        yaxis_title='Valores Acumulados (%)'
    )
    return fig

# Função principal que roda a aplicação


def main():
    st.title("Relatório Agregado de Indicadores por Categoria")

    # Filtros para ano e mês
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    selected_year = st.selectbox(
        'Selecione o Ano:', range(2022, current_year + 1), index=2)
    selected_month = st.selectbox(
        'Selecione o Mês:', range(1, 13), index=current_month - 1)

    # IDs das categorias (substitua pelos IDs reais)
    categories = {
        1: 'Apresentação Financeira',
        2: 'Apresentação Pessoas e Tecnologia',
        3: 'Apresentação Clientes',
        4: 'Apresentação Processos'
    }

    # Filtro de categoria
    category_names = list(categories.values())
    selected_category_name = st.selectbox(
        'Selecione a Categoria:', category_names)
    selected_category_id = list(categories.keys())[
        category_names.index(selected_category_name)]

    st.header(f"Categoria: {selected_category_name}")
    df = load_data_for_category(
        selected_year, selected_month, selected_category_id)
    if not df.empty:
        display_data_table(df)
        # Adiciona o gráfico acumulado para a categoria
        fig = create_accumulated_chart(
            df, f"Gráfico Acumulado - {selected_category_name}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write(
            f"Nenhum dado encontrado para a categoria {selected_category_name} no período selecionado.")


if __name__ == "__main__":
    main()
