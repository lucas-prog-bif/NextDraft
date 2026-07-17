import streamlit as st
import pandas as pd
import mysql.connector  # <-- Adicionado

# Criando a função de conexão localmente para não depender de outros arquivos
def criar_conexao():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Troque pelo seu usuário do MySQL se for diferente
        password="Melao123!",  # Troque pela sua senha do MySQL
        database="nextdraft"
    )

# ==========================================
# 📊 INTERAÇÕES DE POSTAGENS
# ==========================================
def alternar_curtida(id_post, username_usuario):
    try:
        conn = criar_conexao()
        cursor = conn.cursor()
        # AJUSTADO: 
        cursor.execute("SELECT 1 FROM curtidas_posts WHERE id_post = %s AND username = %s", (id_post, username_usuario))
        ja_curtiu = cursor.fetchone()
        if ja_curtiu:
            # AJUSTADO: 
            cursor.execute("DELETE FROM curtidas_posts WHERE id_post = %s AND username = %s", (id_post, username_usuario))
            cursor.execute("UPDATE postagens SET curtidas = GREATEST(0, curtidas - 1) WHERE id_post = %s", (id_post,))
        else:
            # AJUSTADO: 
            cursor.execute("INSERT INTO curtidas_posts (id_post, username) VALUES (%s, %s)", (id_post, username_usuario))
            cursor.execute("UPDATE postagens SET curtidas = curtidas + 1 WHERE id_post = %s", (id_post,))
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass

# ==========================================
# 💬 INTERAÇÕES DE COMENTÁRIOS
# ==========================================
def enviar_comentario(id_post, username_usuario, texto, id_resposta=None):
    if texto.strip():
        try:
            conn = criar_conexao()
            cursor = conn.cursor()
            # AJUSTADO: '
            query = "INSERT INTO comentarios_posts (id_post, username, comentario, id_resposta) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (id_post, username_usuario, texto.strip(), id_resposta))
            conn.commit()
            cursor.close()
            conn.close()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar comentário: {e}")

def deletar_comentario(id_comentario):
    try:
        conn = criar_conexao()
        cursor = conn.cursor()
        query = "DELETE FROM comentarios_posts WHERE id_comentario = %s"
        cursor.execute(query, (id_comentario,))
        conn.commit()
        cursor.close()
        conn.close()
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao excluir comentário: {e}")

def alternar_curtida_comentario(id_comentario, username_usuario):
    try:
        conn = criar_conexao()
        cursor = conn.cursor()
        # AJUSTADO: 
        cursor.execute("SELECT 1 FROM curtidas_comentarios WHERE id_comentario = %s AND username = %s", (id_comentario, username_usuario))
        ja_curtiu = cursor.fetchone()
        if ja_curtiu:
            # AJUSTADO: 
            cursor.execute("DELETE FROM curtidas_comentarios WHERE id_comentario = %s AND username = %s", (id_comentario, username_usuario))
            cursor.execute("UPDATE comentarios_posts SET curtidas = GREATEST(0, curtidas - 1) WHERE id_comentario = %s", (id_comentario,))
        else:
            # AJUSTADO: '
            cursor.execute("INSERT INTO curtidas_comentarios (id_comentario, username) VALUES (%s, %s)", (id_comentario, username_usuario))
            cursor.execute("UPDATE comentarios_posts SET curtidas = curtidas + 1 WHERE id_comentario = %s", (id_comentario,))
        conn.commit()
        cursor.close()
        conn.close()
        st.rerun()
    except:
        pass

def alternar_fixar_comentario(id_comentario, estado_atual):
    try:
        conn = criar_conexao()
        cursor = conn.cursor()
        novo_estado = 0 if estado_atual == 1 else 1
        cursor.execute("UPDATE comentarios_posts SET fixado = %s WHERE id_comentario = %s", (novo_estado, id_comentario))
        conn.commit()
        cursor.close()
        conn.close()
        st.rerun()
    except:
        pass

# ==========================================
# 🎨 EXIBIÇÃO TELA DO FEED
# ==========================================
def exibir_feed():
    st.markdown("##### 📢 ANUNCIANTES & DESTAQUES DA SEMANA")
    st.markdown("""
    <div class="stories-container">
        <div class="story-item"><img src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=100" class="story-circle"><span>Nike Football</span></div>
        <div class="story-item"><img src="https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=100" class="story-circle"><span>Centauro</span></div>
        <div class="story-item"><img src="https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=100" class="story-circle"><span>Euro Soccer</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## ⭐ Destaques da Comunidade")
    usuario_atual = st.session_state['username']
    
    if 'comentario_aberto_em' not in st.session_state:
        st.session_state['comentario_aberto_em'] = None
    if 'respondendo_comentario_id' not in st.session_state:
        st.session_state['respondendo_comentario_id'] = None

    try:
        conn = criar_conexao()
        # AJUSTADO: Caso na tabela postagens também use nome_usuario_autor, alteramos aqui. Mantive de acordo com o seu SELECT original do banco.
        df_posts = pd.read_sql("SELECT id_post, username_autor, subtitulo_autor, url_avatar, url_imagem, legenda, curtidas FROM postagens ORDER BY id_post DESC", conn)
        conn.close()
    except:
        df_posts = pd.DataFrame()

    if df_posts.empty:
        st.info("Nenhum post no banco de dados. Rode os INSERTS das postagens no Workbench.")
    else:
        for idx, post in df_posts.iterrows():
            id_p = post['id_post']
            autor_post = post['username_autor']
            
            # Card Principal do Post
            st.markdown(f"""
            <div class="insta-card">
                <div class="card-header"><img src="{post['url_avatar']}" class="card-avatar"><div><strong style="color: #F8FAFC;">@{autor_post}</strong><br><span style="color: #94A3B8; font-size: 12px;">{post['subtitulo_autor']}</span></div></div>
                <img src="{post['url_imagem']}" class="card-img">
                <div class="card-body"><p style="color: #E2E8F0; margin:0;"><b>@{autor_post}</b> {post['legenda']}</p></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botões de Ação do Post
            c_like, c_comm, c_share = st.columns(3)
            with c_like:
                if st.button(f"❤️ {post['curtidas']}", key=f"like_{id_p}", use_container_width=True):
                    alternar_curtida(id_p, usuario_atual)
                    st.rerun()
            with c_comm:
                if st.button("💬 Comentar", key=f"btn_comm_{id_p}", use_container_width=True):
                    st.session_state['comentario_aberto_em'] = None if st.session_state['comentario_aberto_em'] == id_p else id_p
                    st.session_state['respondendo_comentario_id'] = None
                    st.rerun()
            with c_share: 
                st.button("🔗 Compartilhar", key=f"share_{id_p}", use_container_width=True)
            
            # 💬 CAIXA EXPANSÍVEL DE COMENTÁRIOS
            if st.session_state['comentario_aberto_em'] == id_p:
                st.markdown("<div style='background-color: #0F172A; padding: 14px; border-radius: 8px; margin-top: 5px; border-left: 3px solid #38BDF8;'>", unsafe_allow_html=True)
                
                try:
                    conn = criar_conexao()
                    query_comm = f"SELECT * FROM comentarios_posts WHERE id_post = {id_p} ORDER BY fixado DESC, data_criacao ASC"
                    df_all_comm = pd.read_sql(query_comm, conn)
                    conn.close()
                except:
                    df_all_comm = pd.DataFrame()

                if df_all_comm.empty:
                    st.caption("Nenhum comentário ainda. Comece a resenha!")
                else:
                    df_principais = df_all_comm[df_all_comm['id_resposta'].isna()]
                    
                    for _, c_row in df_principais.iterrows():
                        id_c = c_row['id_comentario']
                        is_fixado = c_row['fixado']
                        # AJUSTADO: 
                        autor_comentario = str(c_row['username']).strip()
                        texto_comentario = str(c_row['comentario']).strip()
                        
                        if is_fixado == 1:
                            st.markdown("<span style='color: #F59E0B; font-size: 11px; font-weight: bold;'>📌 FIXADO PELO AUTOR</span>", unsafe_allow_html=True)
                        
                        st.markdown(f"<p style='color: #F1F5F9; font-size: 14px; margin-bottom: 4px;'><b>@{autor_comentario}</b>: {texto_comentario}</p>", unsafe_allow_html=True)
                        
                        cc1, cc2, cc3, cc4, _ = st.columns([1.5, 2.0, 1.5, 1.5, 3.5])
                        with cc1:
                            if st.button(f"👍 {c_row['curtidas']}", key=f"like_c_{id_c}"):
                                alternar_curtida_comentario(id_c, usuario_atual)
                        with cc2:
                            if st.button("↩️ Responder", key=f"resp_c_{id_c}"):
                                st.session_state['respondendo_comentario_id'] = id_c
                                st.rerun()
                        with cc3:
                            if usuario_atual == post['username_autor']:
                                txt_fixar = "📌 Unfix" if is_fixado == 1 else "📌 Fixar"
                                if st.button(txt_fixar, key=f"fix_c_{id_c}"):
                                    alternar_fixar_comentario(id_c, is_fixado)
                        with cc4:
                            if usuario_atual == autor_comentario or usuario_atual == post['username_autor']:
                                if st.button("🗑️", key=f"del_c_{id_c}", help="Excluir Comentário"):
                                    deletar_comentario(id_c)
                        
                        df_respostas = df_all_comm[df_all_comm['id_resposta'] == id_c]
                        for _, r_row in df_respostas.iterrows():
                            id_resp = r_row['id_comentario']
                            # AJUSTADO: 
                            autor_resp = str(r_row['username']).strip()
                            texto_resposta = str(r_row['comentario']).strip()
                            
                            st.markdown(f"""
                            <div style='margin-left: 25px; margin-top: 6px; margin-bottom: 4px; padding-left: 8px; border-left: 2px solid #334155;'>
                                <p style='color: #CBD5E1; font-size: 13px; margin: 0;'>↳ <b>@{autor_resp}</b>: {texto_resposta}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            rc1, rc2, _ = st.columns([1.5, 1.5, 7.0])
                            with rc1:
                                if st.button(f"👍 {r_row['curtidas']}", key=f"like_resp_{id_resp}"):
                                    alternar_curtida_comentario(id_resp, usuario_atual)
                            with rc2:
                                if usuario_atual == autor_resp or usuario_atual == post['username_autor']:
                                    if st.button("🗑️", key=f"del_resp_{id_resp}", help="Excluir Resposta"):
                                        deletar_comentario(id_resp)
                        
                        st.markdown("<hr style='margin: 12px 0; border-color: #1E293B;'>", unsafe_allow_html=True)

                st.markdown("---")
                
                id_pai = st.session_state['respondendo_comentario_id']
                if id_pai:
                    st.info(f"Respondendo ao comentário selecionado...")
                    texto_sub = "Escreva sua resposta..."
                    btn_label = "Enviar Resposta"
                else:
                    texto_sub = "Escreva um comentário geral..."
                    btn_label = "Comentar"
                
                novo_texto = st.text_input(texto_sub, key=f"input_text_{id_p}")
                
                c_env1, c_env2 = st.columns([2, 8])
                with c_env1:
                    if st.button(btn_label, key=f"submit_c_{id_p}", type="primary"):
                        enviar_comentario(id_p, usuario_atual, novo_texto, id_pai)
                        st.session_state['respondendo_comentario_id'] = None
                        st.rerun()
                with c_env2:
                    if id_pai and st.button("Cancelar Resposta", key=f"cancel_r_{id_p}"):
                        st.session_state['respondendo_comentario_id'] = None
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)