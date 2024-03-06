import streamlit as st
import duckdb

def main():
    st.title("Tela de Entrada de Dados")

    # Criar campos de entrada para os dados
    ano = st.number_input("Ano", min_value=1900, max_value=2100, value=2022)
    mes = st.selectbox("Mês", range(1, 13), index=0)
    indicador = st.text_input("Indicador")
    meta = st.number_input("Meta", min_value=0.0, value=0.0)

    # Botão para enviar os dados
    if st.button("Enviar"):
        # Chamar a função para salvar os dados no banco de dados
        try:
            save_data(ano, mes, indicador, meta)
            st.success("Dados enviados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar os dados: {e}")

def save_data(ano, mes, indicador, meta):
    # Conectar ao banco de dados (assumindo que já foi criado e está disponível)
    conn = duckdb.connect("data/kpi_analytics_db.duckdb")

    try:
        # Executar uma instrução SQL para inserir os dados na tabela correspondente
        conn.execute(f"""
            INSERT INTO dados_mensais (ano, mes, indicador_id, valor)
            VALUES ({ano}, {mes}, '{indicador}', {meta})
        """)
    except Exception as e:
        # Lidar com erros durante a inserção dos dados
        raise e
    finally:
        # Fechar a conexão com o banco de dados, independentemente de ter havido um erro ou não
        conn.close()

if __name__ == "__main__":
    main()
