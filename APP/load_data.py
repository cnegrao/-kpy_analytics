import streamlit as st

def load_data_page():
    st.title('Load Data')
    
    # Campos para entrada de dados
    year = st.number_input("Year", min_value=1900, max_value=2100)
    month = st.number_input("Month", min_value=1, max_value=12)
    indicator = st.text_input("Indicator")
    target = st.number_input("Target")

    # Botão para enviar dados
    if st.button("Submit"):
        # Lógica para armazenar os dados no banco de dados
        st.success("Data submitted successfully!")
