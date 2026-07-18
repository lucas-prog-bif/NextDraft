import streamlit as st
import mysql.connector  # <-- ADICIONADO

# Criando a função de conexão local para a página de perfil
def criar_conexao():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Seu usuário do MySQL
        password="Melao123!",  # Sua senha do MySQL
        database="nextdraft"
    )

def exibir_perfil():
    usuario_atual = st.session_state['username']
    
    st.markdown(f"### 👤 Perfil de @{usuario_atual}")
    st.markdown("Altere suas informações abaixo para que outros atletas te conheçam no feed.")
    st.markdown("---")
    
    # 1. Carregar dados atuais do banco de dados
    try:
        conn = criar_conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT url_avatar, biografia, posicao, time_coracao FROM usuarios WHERE username = %s", (usuario_atual,))
        dados_usuario = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        dados_usuario = None
        st.error(f"Erro ao conectar ao banco: {e}")
        
    # Valores padrão caso o usuário não tenha dados salvos ainda
    avatar_atual = dados_usuario['url_avatar'] if dados_usuario and dados_usuario['url_avatar'] else 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150'
    bio_atual = dados_usuario['biografia'] if dados_usuario and dados_usuario['biografia'] else ''
    posicao_atual = dados_usuario['posicao'] if dados_usuario and dados_usuario['posicao'] else 'Não Informada'
    time_atual = dados_usuario['time_coracao'] if dados_usuario and dados_usuario['time_coracao'] else ''

    # 2. Formulário Visual de Edição
    col_foto, col_campos = st.columns([1, 2])
    
    with col_foto:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='text-align: center;'>
            <img src="{avatar_atual}" style='width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 3px solid #38BDF8; padding: 3px;'>
            <p style='color: #94A3B8; font-size: 12px; margin-top: 8px;'>Sua foto atual</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_campos:
        novo_avatar = st.text_input("🔗 URL da Foto de Perfil", value=avatar_atual)
        
        lista_posicoes = ["Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Ponta", "Centroavante", "Não Informada"]
        idx_pos = lista_posicoes.index(posicao_atual) if posicao_atual in lista_posicoes else 7
        nova_posicao = st.selectbox("🏃 Posição Tática", lista_posicoes, index=idx_pos)
        
        novo_time = st.text_input("🏟️ Time do Coração / Pelada", value=time_atual)

    nova_bio = st.text_area("📝 Biografia (Fale um pouco sobre seu futebol)", value=bio_atual, max_chars=160)

    # 3. Botão de Salvar
    if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
        try:
            conn = criar_conexao()
            cursor = conn.cursor()
            query = """
                UPDATE usuarios 
                SET url_avatar = %s, biografia = %s, posicao = %s, time_coracao = %s 
                WHERE username = %s
            """
            cursor.execute(query, (novo_avatar.strip(), nova_bio.strip(), nova_posicao, novo_time.strip(), usuario_atual))
            conn.commit()
            cursor.close()
            conn.close()
            
            st.success("✅ Perfil atualizado com sucesso! Atualizando a página...")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar no banco de dados: {e}")