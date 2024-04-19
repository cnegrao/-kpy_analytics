import streamlit as st
import pandas as pd
import duckdb
import plotly.graph_objects as go
import os
import sys
from babel.numbers import format_decimal
from babel.dates import format_date
import datetime

def create_chart(df, chart_type, x, y, names, colors, title, xaxis_title, yaxis_title):
    fig = go.Figure()
    for i, data_name in enumerate(names):
        if chart_type[i] == 'Bar':
            fig.add_trace(go.Bar(x=df[x], y=df[data_name], name=names[i], marker_color=colors[i]))
        elif chart_type[i] == 'Scatter':
            fig.add_trace(go.Scatter(x=df[x], y=df[data_name], mode='lines+markers', name=names[i], line=dict(color=colors[i], width=2)))
    fig.update_layout(title_text=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    return fig

def load_data_from_db(query):
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        return pd.read_sql_query(query, conn)

def format_monthly_data(df):
    df['Mês'] = df['month'].apply(lambda x: format_date(datetime.date(x, 1, 1), format='MMM', locale='pt_BR'))
    df.drop(columns='month', inplace=True)
    return df

def calculate_indicators(df):
    df['Desvio (%)'] = df.apply(lambda row: format_decimal((row['Real'] - row['Meta']) / row['Meta'] * 100, format="#,##0.##", locale='pt_BR') if row['Meta'] > 0 else pd.NA, axis=1)
    df['Real Acumulado'] = df['Real'].cumsum()
    df['Meta Acumulada'] = df['Meta'].cumsum()
    df['Desvio Acumulado (%)'] = df.apply(lambda row: format_decimal((row['Real Acumulado'] - row['Meta Acumulada']) / row['Meta Acumulada'] * 100, format="#,##0.##", locale='pt_BR') if row['Meta Acumulada'] > 0 else pd.NA, axis=1)
    df['Farol'] = df['Desvio (%)'].apply(lambda value: '' if pd.isna(value) else '🔵' if float(value.replace(',', '.')) > 110 else '🟢' if float(value.replace(',', '.')) >= 100 else '🟠' if float(value.replace(',', '.')) >= 85 else '🔴')
    df['Farol Acumulado'] = df['Desvio Acumulado (%)'].apply(lambda value: '' if pd.isna(value) else '🔵' if float(value.replace(',', '.')) > 110 else '🟢' if float(value.replace(',', '.')) >= 100 else '🟠' if float(value.replace(',', '.')) >= 85 else '🔴')
    
    # Novos cálculos para Lucratividade
    df['Lucratividade Mensal (%)'] = df['Desvio (%)']  # Exemplo, ajuste conforme a regra específica de negócio
    df['Lucratividade Acumulada (%)'] = df['Desvio Acumulado (%)']  # Exemplo, ajuste conforme necessário

    return df

# Funções plot_lucratividade_mensal e plot_lucratividade_acumulada permanecem inalteradas

# Função display_data_table permanece inalterada

def main():
    st.title("Relatórios de Desempenho")

    print("Diretório atual:", os.getcwd())
    print("Caminho de busca do Python:", sys.path)
    
    indicators_df = load_data_from_db("SELECT id, kpi_name FROM tb_kpi ORDER BY kpi_name")
    selected_indicator_id = st.selectbox('Selecione o indicador:', indicators_df['id'], format_func=lambda x: indicators_df[indicators_df['id'] == x]['kpi_name'].iloc[0])

    years = load_data_from_db(f"SELECT DISTINCT year FROM tb_monthly_data WHERE kpi_id = {selected_indicator_id} ORDER BY year")['year'].tolist()
    if years:
        selected_year = st.selectbox('Selecione o ano:', years)
        monthly_data = load_data_from_db(f"SELECT month, goal as Meta, value as Real FROM tb_monthly_data WHERE kpi_id = {selected_indicator_id} AND year = {selected_year} ORDER BY month ASC")
        monthly_data = format_monthly_data(monthly_data)
        indicators_data = calculate_indicators(monthly_data)
        display_data_table(indicators_data)

        col1, col2= st.columns(2)

        with col1:
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
