import locale
import datetime
import streamlit as st
import pandas as pd
import duckdb
import plotly.graph_objects as go
import os
import sys

# Configuração do locale para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def get_db_connection():
    # Verifica se está em ambiente de produção (ajuste a variável de ambiente conforme necessário)
    if os.getenv('PRODUCTION'):
        db_path = '/mount/src/-kpy_analytics/APP/data/kpi_analytics_db.duckdb'
    else:
        # Caminho local
        db_path = os.path.join(os.getcwd(), 'APP', 'data',
                               'kpi_analytics_db.duckdb')

    # print(f"Connecting to database at: {db_path}")

    try:
        return duckdb.connect(db_path)
    except Exception as e:
        print(f"Failed to connect to the database at {db_path}. Error: {e}")
        raise  # Relança o erro para cima para que possa ser tratado ou registrado em outro lugar


def create_chart(df, chart_type, x, y, names, colors, title, xaxis_title, yaxis_title):
    fig = go.Figure()
    for i, data_name in enumerate(names):
        if chart_type[i] == 'Bar':
            fig.add_trace(
                go.Bar(x=df[x], y=df[data_name], name=names[i], marker_color=colors[i]))
        elif chart_type[i] == 'Scatter':
            fig.add_trace(go.Scatter(
                x=df[x], y=df[data_name], mode='lines+markers', name=names[i], line=dict(color=colors[i], width=2)))
    fig.update_layout(title_text=title, xaxis_title=xaxis_title,
                      yaxis_title=yaxis_title)
    return fig


def load_data_from_db(query):
    try:
        with get_db_connection() as conn:
            print(query)
            return pd.read_sql_query(query, conn)
    except Exception as e:
        print("Erro ao carregar dados:", e)
        return pd.DataFrame()


def format_monthly_data(df):
    df['Mês'] = df['month'].apply(lambda x: pd.to_datetime(
        f'{x}-01', format='%m-%d').strftime('%b'))
    df.drop(columns='month', inplace=True)
    return df


def calculate_indicators(df):

    print(df)
    # Calculando os desvios percentuais
    df['Desvio (%)'] = df.apply(
        lambda row: ((row['Real'] - row['Meta']) / row['Meta']
                     * 100) if row['Meta'] > 0 else None,
        # lambda row: ((row['Real'] / row['Meta'])*100)  if row['Meta'] > 0 else None,
        axis=1
    )

    # Calculando o desvio acumulado
    df['Real Acumulado'] = df['Real'].cumsum().apply(lambda x: round(x, 2))
    df['Meta Acumulada'] = df['Meta'].cumsum().apply(lambda x: round(x, 2))
    # df['Real Acumulado'] = df['Real'].cumsum()
    # df['Meta Acumulada'] = df['Meta'].cumsum()

    df['Desvio Acumulado (%)'] = df.apply(
        lambda row: ((row['Real Acumulado'] - row['Meta Acumulada']) /
                     row['Meta Acumulada'] * 100) if row['Meta Acumulada'] > 0 else None,
        axis=1
    )

    # Debug: Imprime os desvios para verificar os valores
    # print(df[['Desvio (%)', 'Desvio Acumulado (%)']])

   # Calculando o atingimento de meta em percentual
    df['Atingimento de Meta (%)'] = df.apply(
        lambda row: (row['Real'] / row['Meta'] *
                     100) if row['Meta'] > 0 else None,
        axis=1
    )

    # Aplicando os faróis baseado no atingimento de meta
    df['Farol'] = df['Atingimento de Meta (%)'].apply(
        lambda value: '' if value is None else
                      '🔵' if value > 110 else
                      '🟢' if value >= 100 else
                      '🟡' if value >= 85 else
                      '🔴' if value < 85 else 'Error'
    )

   # Calculando o atingimento acumulado de meta em percentual
    df['Atingimento Acumulado de Meta (%)'] = df.apply(
        lambda row: (row['Real Acumulado'] / row['Meta Acumulada']
                     * 100) if row['Meta Acumulada'] > 0 else None,
        axis=1
    )

    df['Farol Acumulado'] = df['Atingimento Acumulado de Meta (%)'].apply(
        lambda value: '' if value is None else
                      '🔵' if value > 110 else
                      '🟢' if 100 <= value <= 110 else
                      '🟡' if 85 <= value < 100 else
                      '🔴' if value < 85 else 'Error'
    )

    # Novos cálculos para Lucratividade
    # Exemplo, ajuste conforme a regra específica de negócio
    df['Lucratividade Mensal (%)'] = df['Desvio (%)']
    # Exemplo, ajuste conforme necessário
    df['Lucratividade Acumulada (%)'] = df['Desvio Acumulado (%)']

    return df


def plot_lucratividade_mensal(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Mês'], y=df['Lucratividade Mensal (%)'],
                  mode='lines+markers', name='Lucratividade Mensal', line=dict(color='green', width=2)))
    fig.update_layout(title='Lucratividade Mensal por Mês',
                      xaxis_title='Mês', yaxis_title='Lucratividade (%)')
    return fig


def plot_lucratividade_acumulada(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Mês'], y=df['Lucratividade Acumulada (%)'],
                  mode='lines+markers', name='Lucratividade Acumulada', line=dict(color='purple', width=2)))
    fig.update_layout(title='Lucratividade Acumulada por Mês',
                      xaxis_title='Mês', yaxis_title='Lucratividade Acumulada (%)')
    return fig


def display_data_table(df):
    # Cópia do DataFrame para manipulação
    df_formatted = df.copy()

    # Formatação dos campos de desvio para percentual com duas casas decimais ou vazio, caso não aplicável
    df_formatted['Meta'] = df_formatted['Meta'].apply(
        lambda x: f"{x * 100:.2f}%")
    df_formatted['Real'] = df_formatted['Real'].apply(
        lambda x: f"{x * 100:.2f}%")
    df_formatted['Meta Acumulada'] = df_formatted['Meta Acumulada'].apply(
        lambda x: f"{x * 100:.2f}%")
    df_formatted['Real Acumulado'] = df_formatted['Real Acumulado'].apply(
        lambda x: f"{x * 100:.2f}%")
    df_formatted['Desvio (%)'] = df_formatted['Desvio (%)'].apply(
        lambda x: '' if pd.isna(x) else f"{x:.2f}%")
    df_formatted['Desvio Acumulado (%)'] = df_formatted['Desvio Acumulado (%)'].apply(
        lambda x: '' if pd.isna(x) else f"{x:.2f}%")

    # Configurações visuais da tabela
    header_color = 'navy'  # Cor de fundo do cabeçalho
    cell_color = 'lightgrey'  # Cor de fundo das células
    text_color = 'white'  # Cor do texto
    font_size = 12  # Tamanho da fonte
    print(df_formatted)
    # Criação da tabela Plotly
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Mês', 'Meta', 'Real', 'Desvio (%)', 'Farol', 'Meta Acumulada',
                    'Real Acumulado', 'Desvio Acumulado (%)', 'Farol Acumulado'],
            fill_color=header_color,
            font=dict(color=text_color, size=font_size+2),
            align='left'
        ),
        cells=dict(
            values=[df_formatted[col] for col in ['Mês', 'Meta', 'Real',
                                                  'Desvio (%)', 'Farol', 'Meta Acumulada', 'Real Acumulado', 'Desvio Acumulado (%)', 'Farol Acumulado']],
            # Aplica a cor de fundo para todas as células
            fill_color=[cell_color]*9,
            # Altera a cor do texto para preto para melhor legibilidade
            font=dict(color='black', size=font_size),
            align='left'
        )
    )])

    # Ajustes finais de layout
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))

    # Exibição da tabela no Streamlit
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.title("Relatórios de Desempenho")

    # print("Diretório2 atual:", os.getcwd())
    # print("Caminho de busca do Python:", sys.path)

    indicators_df = load_data_from_db(
        "SELECT DISTINCT kpi.id, kpi.kpi_name FROM tb_kpi AS kpi INNER JOIN tb_monthly_data AS data ON kpi.id = data.kpi_id ORDER BY kpi.kpi_name")
    selected_indicator_id = st.selectbox(
        'Selecione o indicador:', indicators_df['id'], format_func=lambda x: indicators_df[indicators_df['id'] == x]['kpi_name'].iloc[0])

    years = load_data_from_db(
        f"SELECT DISTINCT year FROM tb_monthly_data WHERE kpi_id = {selected_indicator_id} ORDER BY year")['year'].tolist()
    if years:
        selected_year = st.selectbox('Selecione o ano:', years)
        monthly_data = load_data_from_db(
            f"SELECT month, goal as Meta, value as Real FROM tb_monthly_data WHERE kpi_id = {selected_indicator_id} AND year = {selected_year} ORDER BY month ASC")
        monthly_data = format_monthly_data(monthly_data)
        indicators_data = calculate_indicators(monthly_data)
        display_data_table(indicators_data)

        # Início da seção de colunas para gráficos
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico Metas vs Realizados
            fig1 = create_chart(indicators_data,
                                chart_type=['Bar', 'Scatter'],
                                x='Mês',
                                y=['Real', 'Meta'],
                                names=['Real', 'Meta'],
                                colors=['red', 'blue'],
                                title='Real vs Meta',
                                xaxis_title='Mês',
                                yaxis_title='Valor')
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Gráfico Real Acumulado vs Meta Acumulada
            fig2 = create_chart(indicators_data,
                                chart_type=['Scatter', 'Scatter'],
                                x='Mês',
                                y=['Real Acumulado', 'Meta Acumulada'],
                                names=['Real Acumulado', 'Meta Acumulada'],
                                colors=['crimson', 'navy'],
                                title='Real Acumulado vs Meta Acumulada',
                                xaxis_title='Mês',
                                yaxis_title='Valor Acumulado')
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig3 = plot_lucratividade_mensal(indicators_data)
            st.plotly_chart(fig3, use_container_width=True)
        with col4:
            fig4 = plot_lucratividade_acumulada(indicators_data)
            st.plotly_chart(fig4, use_container_width=True)


if __name__ == "__main__":
    main()
