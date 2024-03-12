import streamlit as st
import data_entry
import reports
import analytics  # Importe a nova página analytics.py

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Minha Aplicação Streamlit",
        page_icon=":chart_with_upwards_trend:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Barra lateral para navegação entre as páginas
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Escolha uma opção:", ["Tela Principal", "Entrada de Dados", "Consulta Analítica", "Análise Acumulada"])  # Adicione a nova página à barra lateral

    # Variável de controle para mostrar ou não o título
    show_title = True

    # Roteamento para diferentes páginas
    if page == "Entrada de Dados":
        data_entry.main()
        show_title = False  # Não mostrar título nas outras páginas
    elif page == "Consulta Analítica":
        reports.main()
        show_title = False  # Não mostrar título nas outras páginas
    elif page == "Análise Acumulada":  # Adicione a nova condição para a nova página
        analytics.main()  # Chame a função main() da página analytics.py
        show_title = False  # Não mostrar título nas outras páginas

    # Se estamos na página principal e a variável de controle é verdadeira, mostramos o título
    if page == "Tela Principal" and show_title:
        show_main_page()

def show_main_page():
    # Título e descrição da tela principal
    st.title("Bem-vindo à minha aplicação")
    st.write("""
        Esta é a tela principal da aplicação. 
        Você pode encontrar várias funcionalidades aqui.
    """)

if __name__ == "__main__":
    main()
