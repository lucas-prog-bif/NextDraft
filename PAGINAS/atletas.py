import streamlit as st
import pandas as pd
from app_nextdraft import criar_conexao

def exibir_atletas():
    st.title("🏃 Vitrine e Busca de Atletas (Base & Várzea)")
    st.markdown("Lista de atletas ativos extraída do seu MySQL:")
    
    try:
        conn = criar_conexao()
        df_atletas_reais = pd.read_sql("SELECT nome_usuario, email, subtitulo_autor FROM usuarios WHERE perfil_tipo = 'atleta'", conn)
        conn.close()
        
        if df_atletas_reais.empty:
            st.warning("Nenhum atleta listado no banco de dados atualmente.")
        else:
            st.dataframe(df_atletas_reais, use_container_width=True, column_config={
                "nome_usuario": "Jogador",
                "email": "E-mail de Contato",
                "subtitulo_autor": "Categoria / Scout"
            })
    except Exception as e:
        st.error(f"Erro ao conectar com a tabela do MySQL: {e}")