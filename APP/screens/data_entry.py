import streamlit as st
import duckdb

def main():
    st.title("Tela de Entrada de Dados")

    indicators = load_indicators()
    selected_indicator_id, selected_indicator_name = st.selectbox('Selecione o indicador:', indicators, format_func=lambda x: x[1])

    st.write("Ano e Mês:")
    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input("Ano", min_value=2024, max_value=2025, value=2024)
    with col2:
        month = st.selectbox("Mês", range(1, 13), index=0)

    st.write("Meta e Valor:")
    col3, col4 = st.columns(2)
    with col3:
        value = st.number_input("Valor", min_value=0.0, value=0.0)
    with col4:
        goal = st.number_input("Meta", min_value=0.0, value=0.0)

    if st.button("Enviar"):
        try:
            save_data(year, month, selected_indicator_id, goal, value)
        except Exception as e:
            # Aqui, o tratamento de exceção já foi feito em `save_data`, então pode-se optar por logar ou realizar ações adicionais se necessário.
            pass  # Ou realizar alguma ação adicional se necessário

def load_indicators():
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        indicators = conn.execute("SELECT id, kpi_name FROM tb_kpi").fetchall()
    return [(indicator[0], indicator[1]) for indicator in indicators]

def save_data(year, month, selected_indicator_id, goal, value):
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        try:
            conn.execute("""
                INSERT INTO tb_monthly_data (kpi_id, year, month, goal, value)
                VALUES (?, ?, ?, ?, ?)
            """, (selected_indicator_id, year, month, goal, value))
            st.success("Dados enviados com sucesso!")
        except duckdb.OperationalError as e:
            if "unique constraint" in str(e).lower():
                st.error("Erro: Os dados já existem para o indicador, ano e mês fornecidos.")
            else:
                st.error(f"Erro ao enviar os dados: {e}")
        except Exception as e:
            st.error(f"Erro ao enviar os dados: {e}")

if __name__ == "__main__":
    main()
