import streamlit as st
import data_entry
import reports

def main():
    st.title("Bem-vindo à minha aplicação")

    st.write("""
        Esta é a tela principal da aplicação. 
        Você pode encontrar várias funcionalidades aqui.
    """)

    # Links para outras partes da aplicação
    if st.button("Ir para a tela de entrada de dados"):
        # Redirecionar para a tela de entrada de dados
        st.write("Redirecionando para a tela de entrada de dados...")
        redirect_to_data_entry()

    if st.button("Ir para a tela de consulta analítica"):
        # Redirecionar para a tela de consulta analítica
        st.write("Redirecionando para a tela de consulta analítica...")
        redirect_to_reports()

def redirect_to_data_entry():
    # Redirecionar para a página de entrada de dados (data_entry.py)
    # Você pode chamar a função que renderiza a página de entrada de dados aqui
    data_entry.main()

def redirect_to_reports():
    # Redirecionar para a página de consulta analítica (reports.py)
    # Você pode chamar a função que renderiza a página de consulta analítica aqui
    reports.main()

if __name__ == "__main__":
    main()
