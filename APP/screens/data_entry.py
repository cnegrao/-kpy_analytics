import os
import streamlit as st
import duckdb
from datetime import datetime

# Obtém o mês atual
current_month = datetime.now().month
current_year = datetime.now().year
# Função para obter a conexão com o banco de dados


def get_db_connection():
    # Determina o caminho do banco de dados com base no ambiente
    print("Diretório atual de trabalho:", os.getcwd())
    print("Caminho absoluto do script:", os.path.abspath(__file__))
    print("Diretório do script:", os.path.dirname(os.path.abspath(__file__)))

    if os.getenv('PRODUCTION'):
        # Caminho em ambiente de produção
        db_path = '/mount/src/-kpy_analytics/APP/data/kpi_analytics_db.duckdb'
    else:
        # Caminho local para desenvolvimento
        db_path = os.path.join(os.getcwd(), 'APP', 'data',
                               'kpi_analytics_db.duckdb')

    print(f"Connecting to database at: {db_path}")

    try:
        # Tenta conectar ao banco de dados e retorna a conexão
        connection = duckdb.connect(db_path)
        print("Connection successful!")
        return connection
    except Exception as e:
        # Caso ocorra um erro, exibe e relança
        print(f"Failed to connect to the database at {db_path}. Error: {e}")
        raise


# Função para carregar indicadores
def load_indicators():
    with get_db_connection() as conn:
        indicators = conn.execute(
            "SELECT id, kpi_name FROM tb_kpi order by kpi_name").fetchall()
    return [(indicator[0], indicator[1]) for indicator in indicators]

# Função para salvar os dados inseridos


def save_data(year, month, selected_indicator_id, goal, value):
    try:
        # Formatando goal e value para duas casas decimais
       # Formatando goal e value para duas casas decimais
        goal = round(float(goal), 2)
        value = round(float(value), 2)

        with get_db_connection() as conn:
            # Verifica se já existe um registro para este indicador no mês e ano especificados
            existing = conn.execute("SELECT * FROM tb_monthly_data WHERE kpi_id = ? AND year = ? AND month = ?",
                                    (selected_indicator_id, year, month)).fetchall()
            if existing:
                st.error(
                    "Erro: Já existe registro para o indicador selecionado no período especificado. Por favor, verifique e tente novamente.")
                return

            # Insere os novos dados se não houver duplicidade
            conn.execute("INSERT INTO tb_monthly_data (kpi_id, year, month, goal, value) VALUES (?, ?, ?, ?, ?)",
                         (selected_indicator_id, year, month, goal, value))
            st.success("Dados enviados com sucesso! ✅")
    except duckdb.OperationalError as e:
        st.error(
            "Erro técnico ao enviar os dados. Por favor, tente novamente ou contate o suporte.")
    except Exception as e:
        st.error(f"Erro ao enviar os dados: {e}")


# Função principal que roda a aplicação
def main():
    st.title("Tela de Entrada de Dados 📊")

    with st.container():
        st.subheader("Selecione o Indicador 🔍")
        indicators = load_indicators()
        selected_indicator_id, selected_indicator_name = st.selectbox(
            'Escolha um indicador:', indicators, format_func=lambda x: x[1])

    with st.container():
        st.subheader("Informe o Período 📅")
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input(
                "Ano", min_value=2024, max_value=2026, value=current_year, help="Selecione o ano desejado.")
        with col2:
            month = st.number_input(
                "Mês", min_value=1, max_value=12, value=current_month, help="Selecione o mês desejado.")

    with st.container():
        st.subheader("Defina Valor e Meta 💹")
        col3, col4 = st.columns(2)
        with col3:
            value = st.number_input(
                "Valor", min_value=0.01, value=0.01, step=0.01, help="Insira o valor alcançado.")
        with col4:
            goal = st.number_input(
                "Meta", min_value=0.01, value=0.01, step=0.01, help="Insira a meta estabelecida.")

    submit_button = st.button("Enviar Dados 🚀")
    if submit_button:
        save_data(year, month, selected_indicator_id, goal, value)


if __name__ == "__main__":
    main()
