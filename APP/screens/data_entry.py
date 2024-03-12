import streamlit as st
import duckdb

def main():
    show_main_title = False  # Definir como False para não exibir o título principal
    st.title("Tela de Entrada de Dados")

    # Carregar os indicadores para preencher o dropdown
    indicators = load_indicators()
    selected_indicator_id, selected_indicator_name = st.selectbox('Selecione o indicador:', indicators, format_func=lambda x: x[1])
    print(selected_indicator_id)
    print(selected_indicator_name)
    # Campos para preencher os dados (Ano e Mês)
    st.write("Ano e Mês:")
    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input("Ano", min_value=2024, max_value=2025, value=2024)
    with col2:
        month = st.selectbox("Mês", range(1, 13), index=0)

    # Campos para preencher os dados (Meta e Valor)
    st.write("Meta e Valor:")
    col3, col4 = st.columns(2)
    with col3:
        value = st.number_input("Valor", min_value=0.0, value=0.0)
    with col4:
         goal = st.number_input("Meta", min_value=0.0, value=0.0)
    
    # Botão para enviar os dados
    if st.button("Enviar"):
        # Chamar a função para salvar os dados no banco de dados
        try:
            save_data(year, month, selected_indicator_id, goal, value)
            st.success("Dados enviados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar os dados: {e}")

def load_indicators():
    # Utilizar o gerenciador de contexto para a conexão ao banco de dados
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        # Executar uma consulta SQL para obter os indicadores da tabela tb_kpi
        indicators = conn.execute("SELECT id, kpi_name FROM tb_kpi").fetchall()

    # Retornar os indicadores no formato (id, nome)
    return [(indicator[0], indicator[1]) for indicator in indicators]

def save_data(year, month, selected_indicator_id, goal, value):
    # Utilizar o gerenciador de contexto para a conexão ao banco de dados
    with duckdb.connect("app/data/kpi_analytics_db.duckdb") as conn:
        try:
            # Executar uma instrução SQL para inserir os dados na tabela correspondente
            # Utilizando uma query parametrizada para evitar SQL Injection
            conn.execute("""
                INSERT INTO tb_monthly_data (kpi_id, year, month, goal, value)
                VALUES (?, ?, ?, ?, ?)
            """, (selected_indicator_id, year, month, goal, value))
        except duckdb.OperationalError as e:
            if "unique constraint" in str(e).lower():
                st.error("Erro: Os dados já existem para o indicador, ano e mês fornecidos.")
            else:
                st.error(f"Erro ao enviar os dados: {e}")
        except Exception as e:
            # Lidar com outros erros específicos ou propagá-los
            st.error(f"Erro ao enviar os dados: {e}")

if __name__ == "__main__":
    main()
