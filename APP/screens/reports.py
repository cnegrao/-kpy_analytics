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

def create_chart(df, chart_type, x, y, names, colors, title, xaxis_title, yaxis_title):
    fig = go.Figure()
    for i, data_name in enumerate(names):
        if chart_type[i] == 'Bar':
            fig.add_trace(go.Bar(x=df[x], y=df[data_name], name=names[i], marker_color=colors[i]))
        elif chart_type[i] == 'Scatter':
            fig.add_trace(go.Scatter(x=df[x], y=df[data_name], mode='lines+markers', name=names[i], line=dict(color=colors[i], width=2)))
    fig.update_layout(title_text=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    return fig

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'data', 'kpi_analytics_db.duckdb')
    return duckdb.connect(db_path)

def load_data_from_db(query):
    with get_db_connection() as conn:
        return pd.read_sql_query(query, conn)

def format_monthly_data(df):
    df['Mês'] = df['month'].apply(lambda x: pd.to_datetime(f'{x}-01', format='%m-%d').strftime('%b'))
    df.drop(columns='month', inplace=True)
    return df

def calculate_indicators(df):
    df['Desvio (%)'] = df.apply(
        lambda row: ((row['Real'] - row['Meta']) / row['Meta'] * 100) if row['Meta'] > 0 else None,
        axis=1
    )
    df['Real Acumulado'] = df['Real'].cumsum()
    df['Meta Acumulada'] = df['Meta'].cumsum()
    df['Desvio Acumulado (%)'] = df.apply(
        lambda row: ((row['Real Acumulado'] - row['Meta Acumulada']) / row['Meta Acumulada'] * 100) if row['Meta Acumulada'] > 0 else None,
        axis=1
    )
    # Atingimento de Meta em Percentual
    df['Atingimento de Meta (%)'] = df.apply(
        lambda row: (row['Real'] / row['Meta'] * 100) if row['Meta'] > 0 else None,
        axis=1
    )
    # Farol baseado no atingimento de Meta
    df['Farol'] = df['Atingimento de Meta (%)'].apply(
        lambda value: '' if value is None else
                      '🔵' if value > 110 else
                      '🟢' if value >= 100 else
                      '🟡' if 85 <= value < 100 else
                      '🔴' if value < 85 else 'Error'
    )
    return df

def display_data_table(df):
    df_formatted = df.copy()
    df_formatted['Desvio (%)'] = df_formatted['Desvio (%)'].apply(lambda x: '' if pd.isna(x) else f"{x:.2f}%")
    df_formatted['Desvio Acumulado (%)'] = df_formatted['Desvio Acumulado (%)'].apply(lambda x: '' if pd.isna(x) else f"{x:.2f}%")
    header_color = 'navy'
    cell_color = 'lightgrey'
    text_color = 'white'
    font_size = 12
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Mês', 'Meta', 'Real', 'Desvio (%)', 'Meta Acumulada', 'Real Acumulado', 'Desvio Acumulado (%)', 'Atingimento de Meta (%)', 'Farol'],
                    fill_color=header_color,
                    font=dict(color=text_color, size=font_size+2),
                    align='left'),
        cells=dict(values=[df_formatted[col] for col in ['Mês', 'Meta', 'Real', 'Desvio (%)', 'Meta Acumulada', 'Real Acumulado', 'Desvio Acumulado (%)', 'Atingimento de Meta (%)', 'Farol']],
                   fill_color=cell_color,
                   font=dict(color='black', size=font_size),
                   align='left')
    )])
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("Relatórios de Desempenho")
    indicators_df = load_data_from_db("""
                                        SELECT DISTINCT kpi.id, kpi.kpi_name 
                                        FROM tb_kpi AS kpi
                                        INNER JOIN tb_monthly_data AS data ON kpi.id = data.kpi_id
                                        ORDER BY kpi.kpi_name
                                        """)
    selected_indicator_id = st.selectbox('Selecione o indicador:', indicators_df['id'], format_func=lambda x: indicators_df[indicators_df['id'] == x]['kpi_name'].iloc[0])
    years = load_data_from_db(f"SELECT DISTINCT year FROM tb_monthly_data WHERE kpi_id = {selected_indicator_id} ORDER BY year")['year'].tolist()
    if years:
        selected_year = st.selectbox('Selecione o ano:', years)
        monthly_data = load_data_from_db(f"SELECT month, goal as Meta, value as Real FROM tb_monthly_data WHERE kpi_id = {selected_indicator_id} AND year = {selected_year} ORDER BY month ASC")
        monthly_data = format_monthly_data(monthly_data)
        indicators_data = calculate_indicators(monthly_data)
        display_data_table(indicators_data)

if __name__ == "__main__":
    main()
