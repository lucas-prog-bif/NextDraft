import streamlit as st
import pandas as pd
from app_nextdraft import criar_conexao


def exibir_quadras():
    st.title("🏟️ Arenas e Quadras Parceiras")
    st.markdown("Complexos esportivos disponíveis para agendamento:")
    
    try:
        conn = criar_conexao()
        df_quadras_reais = pd.read_sql("SELECT nome_usuario, email, subtitulo_autor FROM usuarios WHERE perfil_tipo = 'quadra'", conn)
        conn.close()
        
        if df_quadras_reais.empty:
            dados_quadras = {
                "Nome do Complexo": ["🏟️ Arena Lapa Soccer", "🏟️ Euro Society Bauru"],
                "E-mail Comercial": ["lapa@soccer.com", "euro@society.com"],
                "Localização / Estrutura": ["São Paulo - Lapa", "Bauru - Centro"]
            }
            st.dataframe(pd.DataFrame(dados_quadras), use_container_width=True)
        else:
            st.dataframe(df_quadras_reais, use_container_width=True)
    except:
        st.error("Erro ao carregar arenas.")