import streamlit as st
import pandas as pd
import duckdb
import locale
import plotly.graph_objects as go


# Configuração do locale para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def create_real_vs_meta_chart(df):
    fig = go.Figure()
    
    # Adiciona o Real como barras
    fig.add_trace(go.Bar(x=df['Mês'], y=df['Real'], name='Real', marker_color='red'))
    
    # Adiciona a Meta como linha
    fig.add_trace(go.Scatter(x=df['Mês'], y=df['Meta'], mode='lines+markers', name='Meta', line=dict(color='blue', width=2)))
    
    fig.update_layout(title_text='Real vs Meta', xaxis_title='Mês', yaxis_title='Valor', barmode='group')
    return fig


def create_cumulative_chart(df):
    fig = go.Figure()
    # Usando go.Scatter para criar gráfico de linhas
    fig.add_trace(go.Scatter(x=df['Mês'], y=df['Meta Acumulada'], mode='lines+markers', name='Meta Acumulada', line=dict(color='navy')))
    fig.add_trace(go.Scatter(x=df['Mês'], y=df['Real Acumulado'], mode='lines+markers', name='Real Acumulado', line=dict(color='crimson')))
    fig.update_layout(title_text='Real Acumulado vs Meta Acumulada', xaxis_title='Mês', yaxis_title='Valor Acumulado')
    return fig


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
    """Calcula desvios e aplica o farol para dados mensais e acumulados, tratando corretamente os casos sem dados."""
    # Calcula o desvio somente se a meta for maior que zero; caso contrário, define como NaN
    df['Desvio (%)'] = df.apply(lambda row: (row['Real'] - row['Meta']) / row['Meta'] * 100 if row['Meta'] > 0 else pd.NA, axis=1)
    df['Real Acumulado'] = df['Real'].cumsum()
    df['Meta Acumulada'] = df['Meta'].cumsum()
    df['Desvio Acumulado (%)'] = df.apply(lambda row: (row['Real Acumulado'] - row['Meta Acumulada']) / row['Meta Acumulada'] * 100 if row['Meta Acumulada'] > 0 else pd.NA, axis=1)

    # Define os faróis baseados nas regras de desvio, incluindo o tratamento para quando não há dados (NaN)
    def farol(value):
        if pd.isna(value): return ''  # Não exibe farol quando não há dados
        elif value > 110: return '🔵'
        elif value >= 100: return '🟢'
        elif value >= 85: return '🟠'
        else: return '🔴'

    df['Farol'] = df['Desvio (%)'].apply(farol)
    df['Farol Acumulado'] = df['Desvio Acumulado (%)'].apply(farol)

    # Aplique a formatação como percentual diretamente antes de exibir os dados, não aqui
    df.rename(columns={'month': 'Mês'}, inplace=True)
    return df
    
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
    st.write("Dados Mensais e Acumulados")

    # Aplica a formatação percentual aqui, convertendo NaN para string vazia e formatando números
    data['Desvio (%)'] = data['Desvio (%)'].apply(lambda x: '' if pd.isna(x) else "{:.2f}%".format(x))
    data['Desvio Acumulado (%)'] = data['Desvio Acumulado (%)'].apply(lambda x: '' if pd.isna(x) else "{:.2f}%".format(x))

    # Convertendo o DataFrame para Markdown
    result_md = data.to_markdown(index=False)
    st.markdown(result_md, unsafe_allow_html=True)
    
       # Exibe os gráficos
    real_vs_meta_fig = create_real_vs_meta_chart(data)
    st.plotly_chart(real_vs_meta_fig, use_container_width=True)
    
    cumulative_fig = create_cumulative_chart(data)
    st.plotly_chart(cumulative_fig, use_container_width=True)


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
        st.write("Legenda do Farol:")
    
    # Legenda do Farol ajustada
    st.write("Legenda do Farol:")
    st.markdown("""
    <div style="margin-top: 20px;">
        <div><span style="color: blue;">🔵</span> <b>Azul:</b> Desempenho acima da meta (> 110% da meta)</div>
        <div><span style="color: green;">🟢</span> <b>Verde:</b> Desempenho na meta (≥ 100% da meta e ≤ 110% da meta)</div>
        <div><span style="color: orange;">🟠</span> <b>Laranja:</b> Desempenho próximo da meta (≥ 85% e < 100% da meta)</div>
        <div><span style="color: red;">🔴</span> <b>Vermelho:</b> Desempenho abaixo da meta (≤ 84% da meta)</div>
    </div>
    """, unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()
