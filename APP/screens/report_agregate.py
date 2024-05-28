import streamlit as st
import pandas as pd
import duckdb
import locale
import plotly.graph_objects as go
import os

# Configuração do locale para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def get_db_connection():
    if os.getenv('PRODUCTION'):
        db_path = '/mount/src/-kpy_analytics/APP/data/kpi_analytics_db.duckdb'
    else:
        db_path = os.path.join(os.getcwd(), 'APP', 'data',
                               'kpi_analytics_db.duckdb')

    try:
        return duckdb.connect(db_path)
    except Exception as e:
        print(f"Failed to connect to the database at {db_path}. Error: {e}")
        raise


def load_data():
    query = """
    SELECT kpi_name AS Indicador, unit AS Unidade, direction AS Melhor, 
           meta_mes AS Meta, real_mes AS Real, 
           meta_acumulado AS Meta_Acumulado, real_acumulado AS Real_Acumulado,
           absoluto AS Absoluto, relativo AS Relativo
    FROM tb_kpi_data
    ORDER BY id
    """
    with get_db_connection() as conn:
        return pd.read_sql_query(query, conn)


def calculate_farol(meta, real):
    if real > meta * 1.01:
        return 4
    elif real >= meta:
        return 3
    elif real >= meta * 0.70:
        return 2
    else:
        return 1


def calculate_indicators(df):
    df['Farol'] = df.apply(lambda row: calculate_farol(
        row['Meta'], row['Real']), axis=1)
    df['Farol_Acumulado'] = df.apply(lambda row: calculate_farol(
        row['Meta_Acumulado'], row['Real_Acumulado']), axis=1)
    return df


def display_table(df):
    st.write("Indicadores de Desempenho")

    # Configurações visuais da tabela
    header_color = 'navy'
    cell_color = 'lightgrey'
    text_color = 'white'
    font_size = 12

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color=header_color,
            font=dict(color=text_color, size=font_size+2),
            align='left'
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color=[cell_color]*len(df.columns),
            font=dict(color='black', size=font_size),
            align='left'
        )
    )])

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.title("Relatórios de Desempenho por Categoria")

    df = load_data()
    st.write("Dados carregados:", df.shape)

    df = df.drop_duplicates()
    st.write("Dados após remover duplicatas:", df.shape)

    df = calculate_indicators(df)
    st.write("Dados finais:", df.shape)

    display_table(df)


if __name__ == "__main__":
    main()
