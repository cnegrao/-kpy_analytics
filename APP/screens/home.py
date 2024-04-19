import sys
import os

# Determinar o caminho base com base no sistema operacional
base_path = 'D:\\#kpy_analytics' if os.name == 'nt' else '/mount/src/-kpy_analytics'

# Adicionar o caminho base ao sys.path se ainda não estiver incluído
if base_path not in sys.path:
    sys.path.insert(0, base_path)

from APP.screens import data_entry, reports
import streamlit as st
import os
import sys

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
    page = st.sidebar.radio("Escolha uma opção:", ["Tela Principal", "Entrada de Dados", "Consulta Analítica"])


 
    # Variável de controle para mostrar ou não o título
    show_title = True

    # Roteamento para diferentes páginas
    if page == "Entrada de Dados":
        data_entry.main()
        show_title = False  # Não mostrar título nas outras páginas
    elif page == "Consulta Analítica":
        reports.main()
        show_title = False
        # Se estamos na página principal e a variável de controle é verdadeira, mostramos o título
    if page == "Tela Principal" and show_title:
        show_main_page()

def show_main_page():
    # Título e descrição da tela principal
    st.title("Bem-vindo à minha aplicação")
    st.write("""
        Esta é a tela principal da aplicação. 
        Use o menu à esquerda para navegar entre as diferentes funcionalidades disponíveis.
    """)
    print("Diretório atual:", os.getcwd())
    print("Caminho de busca do Python:", sys.path)

if __name__ == "__main__":
    main()
