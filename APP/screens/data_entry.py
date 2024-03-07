import streamlit as st
import duckdb

def main():
    st.title("Tela de Entrada de Dados")

    # Carregar os indicadores para preencher o dropdown
    indicators = load_indicators()
    selected_indicator_id, selected_indicator_name = st.selectbox('Selecione o indicador:', indicators)

    # Campos para preencher os dados
    year = st.number_input("Ano", min_value=2024, max_value=2025, value=2024)
    month = st.selectbox("Mês", range(1, 13), index=0)
    meta = st.number_input("Meta", min_value=0.0, value=0.0)

    # Botão para enviar os dados
    if st.button("Enviar"):
        # Chamar a função para salvar os dados no banco de dados
        try:
            save_data(year, month, selected_indicator_id, meta)
            st.success("Dados enviados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar os dados: {e}")

@st.cache(hash_funcs={duckdb.DuckDBPyConnection: id})
def load_indicators():
    # Utilizar o gerenciador de contexto para a conexão ao banco de dados
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        # Executar uma consulta SQL para obter os indicadores da tabela tb_kpi
        indicators = conn.execute("SELECT id, kpi_name FROM tb_kpi").fetchall()

    # Retornar os indicadores no formato (id, nome)
    return [(indicator[0], indicator[1]) for indicator in indicators]

def save_data(year, month, selected_indicator_id, meta):
    # Utilizar o gerenciador de contexto para a conexão ao banco de dados
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        try:
            # Executar uma instrução SQL para inserir os dados na tabela correspondente
            # Utilizando uma query parametrizada para evitar SQL Injection
            conn.execute("""
                INSERT INTO tb_monthly_data (kpi_id, year, month, value)
                VALUES (?, ?, ?, ?)
            """, (selected_indicator_id, year, month, meta))
        except Exception as e:
            # Aqui você pode lidar com erros específicos ou apenas propagá-los
            raise e

if __name__ == "__main__":
    main()