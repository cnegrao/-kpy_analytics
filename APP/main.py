import streamlit as st
from load_data import load_data_page

def main():
    st.title('KPI Analytics App')
    
    # Definindo as opções de navegação
    pages = {
        "Load Data": load_data_page
        # Adicione mais páginas aqui conforme necessário
    }

    # Renderiza a barra de navegação lateral
    page = st.sidebar.selectbox("Selecione uma página", tuple(pages.keys()))

    # Renderiza a página selecionada
    pages[page]()

if __name__ == "__main__":
    main()
