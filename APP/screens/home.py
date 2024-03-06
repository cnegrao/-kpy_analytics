import streamlit as st

def main():
    st.title("Bem-vindo à minha aplicação")

    st.write("""
        Esta é a tela principal da aplicação. 
        Você pode encontrar várias funcionalidades aqui.
    """)

    # Adicione links ou botões para outras partes da aplicação
    if st.button("Ir para a tela de entrada de dados"):
        # Redirecionar para a tela de entrada de dados
        st.write("Redirecionando para a tela de entrada de dados...")

    if st.button("Ir para a tela de consulta analítica"):
        # Redirecionar para a tela de consulta analítica
        st.write("Redirecionando para a tela de consulta analítica...")

if __name__ == "__main__":
    main()
