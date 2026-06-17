import streamlit as st
import mysql.connector
import pandas as pd
import dotenv
import os
import hashlib
from datetime import datetime
import plotly.express as px

# 1. CARREGAR CONFIGURAÇÕES DE SEGURANÇA (.env)
dotenv.load_dotenv()

def criar_conexao():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database="nextdraft"
    )

# Funções auxiliares para CRIPTOGRAFIA DE SENHA (Segurança de Mercado)
def criptografar_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def verificar_senha(senha_digitada: str, senha_banco: str) -> bool:
    return criptografar_senha(senha_digitada) == senha_banco

# Configuração inicial da página (Layout centralizado focado em mobile/web app)
st.set_page_config(page_title="NextDraft Ecosystem", page_icon="⚽", layout="centered")

# 🔄 GERENCIADOR DE ESTADO (Navegação instantânea)
if "navegacao_radio" not in st.session_state:
    st.session_state["navegacao_radio"] = "🏠 Início"

def ir_para_cadastro_atleta():
    st.session_state["navegacao_radio"] = "🏃 Área do Atleta"

def ir_para_cadastro_peladeiro():
    st.session_state["navegacao_radio"] = "🍻 Comunidade Peladeiro"

def ir_para_cadastro_parceiro():
    st.session_state["navegacao_radio"] = "🏢 Parceiros & Quadras"

def tela_login():
    st.subheader("🔑 Acesse sua Conta")
    
    aba_atleta, aba_admin = st.tabs(["🏃 Atleta / Peladeiro", "🔐 Administrador"])
    
    with aba_atleta:
        email = st.text_input("E-mail:", key="login_email")
        senha = st.text_input("Senha:", type="password", key="login_senha")
        
        if st.button("Entrar como Jogador"):
            if email and senha:
                try:
                    conn = criar_conexao()
                    cursor = conn.cursor()
                    
                    # Busca primeiro na tabela de atletas
                    cursor.execute("SELECT id_atleta, senha, nome, 'atleta' as tipo FROM atletas WHERE email = %s", (email,))
                    usuario = cursor.fetchone()
                    
                    # Se não achar, busca na tabela de peladeiros
                    if not usuario:
                        cursor.execute("SELECT id_peladeiro, senha, nome, 'peladeiro' as tipo FROM peladeiros WHERE email = %s", (email,))
                        usuario = cursor.fetchone()
                        
                    cursor.close()
                    conn.close()
                    
                    if usuario and verificar_senha(senha, usuario[1]):
                        st.session_state["logado"] = True
                        st.session_state["user_id"] = usuario[0]
                        st.session_state["user_nome"] = usuario[2]
                        st.session_state["user_tipo"] = usuario[3]
                        st.success(f"Bem-vindo de volta, {usuario[2]}!")
                        st.rerun() 
                    else:
                        st.error("E-mail ou senha incorretos.")
                except Exception as e:
                    st.error(f"Erro ao conectar: {e}")
            else:
                st.warning("Preencha todos os campos.")

    with aba_admin:
        admin_email = st.text_input("E-mail do Admin:", key="login_admin_email")
        admin_senha = st.text_input("Senha do Admin:", type="password", key="login_admin_senha")
        
        if st.button("Entrar no Painel Master"):
            if admin_email == os.getenv("ADMIN_USER") and admin_senha == os.getenv("ADMIN_PASS"):
                st.session_state["logado"] = True
                st.session_state["user_nome"] = "Diretoria Master"
                st.session_state["user_tipo"] = "admin"
                st.success("Acesso Administrativo Autorizado!")
                st.rerun()
            else:
                st.error("Credenciais administrativas inválidas.")

# 2. MENU LATERAL DE NAVEGAÇÃO
st.sidebar.title("⚽ NextDraft v2")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

st.sidebar.markdown("---")

if not st.session_state["logado"]:
    menu = st.sidebar.radio(
        "Navegue pelo App:",
        ["🏠 Início", "🔑 Entrar no App"],
        key="navegacao_radio"
    )
else:
    st.sidebar.write(f"Olá, **{st.session_state['user_nome']}**!")
    if st.sidebar.button("🚪 Sair / Logoff"):
        st.session_state["logado"] = False
        st.session_state["user_tipo"] = None
        st.rerun()
        
    menu = st.sidebar.radio(
        "Navegue pelo App:",
        ["🏠 Início", "🏃 Área do Atleta", "🍻 Comunidade Peladeiro", "🏢 Parceiros & Quadras", "🔐 Painel Admin"],
        key="navegacao_radio"
    )

# -----------------------------------------------------------------
# 🏠 TELA INICIAL
# -----------------------------------------------------------------
if menu == "🏠 Início":
    st.title("NextDraft Social")
    st.subheader("A rede social do futebol que conecta a base à várzea.")
    st.write("Crie seu perfil, compartilhe seus atributos e feche contratos ou peladas em uma comunidade ativa.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🏃 Atletas de Base")
        st.write("Monte seu perfil com notas estilo FIFA, ganhe visibilidade e mostre seu futebol para olheiros.")
        st.button("🚀 Ir para Área de Atletas", on_click=ir_para_cadastro_atleta, use_container_width=True)
    with col2:
        st.markdown("### 🍻 Peladeiros")
        st.write("Encontre os melhores rachas, confirme presença nos jogos e interaja no feed da resenha.")
        st.button("⚽ Entrar para a Comunidade", on_click=ir_para_cadastro_peladeiro, use_container_width=True)
    with col3:
        st.markdown("### 🏢 Quadras & Clubes")
        st.write("Divulgue seus horários, publique vagas em aberto e gerencie os atletas da sua escolinha.")
        st.button("🏢 Registrar Estabelecimento", on_click=ir_para_cadastro_parceiro, use_container_width=True)

elif menu == "🔑 Entrar no App":
    st.title("Acesso ao Sistema")
    tela_login()

# -----------------------------------------------------------------
# 🏃 ÁREA DO ATLETA (Estilo Feed do Instagram / Perfis)
# -----------------------------------------------------------------
elif menu == "🏃 Área do Atleta":
    st.title("🏃 Comunidade NextDraft Atletas")
    
    # Abas estilo navegação superior de aplicativo
    aba_feed, aba_cadastro = st.tabs(["📱 Feed de Atletas", "📝 Criar Meu Perfil Técnico"])
    
    with aba_feed:
        st.markdown("### 🔎 Descubra novos talentos")
        try:
            conn = criar_conexao()
            query = """
                SELECT a.id_atleta, a.nome, a.posicao_principal, a.perna_preferida, a.cidade, a.estado,
                       h.nota_velocidade, h.nota_passe, h.nota_fisico, h.nota_finalizacao, h.gols_marcados
                FROM atletas a
                INNER JOIN historico_desempenho h ON a.id_atleta = h.id_atleta
            """
            df = pd.read_sql(query, conn)
            conn.close()
            
            if df.empty:
                st.info("Nenhum post ou atleta listado ainda no feed.")
            else:
                for index, atleta in df.iterrows():
                    # CARD DO INSTAGRAM: Usando container com borda ativa
                    with st.container(border=True):
                        # Topo do Post (Avatar + Nome + Localização)
                        c_avatar, c_user = st.columns([1, 8])
                        with c_avatar:
                            st.image("https://cdn-icons-png.flaticon.com/512/166/166347.png", width=45)
                        with c_user:
                            st.markdown(f"**@{atleta['nome'].lower().replace(' ', '_')}**")
                            st.caption(f"📍 {atleta['cidade']} - {atleta['estado']} | ⚽ {atleta['posicao_principal'].title()}")
                        
                        st.markdown("---")
                        
                        # Corpo do Post (Informações Técnicas organizadas como imagem conceitual)
                        overall = int((atleta['nota_velocidade'] + atleta['nota_passe'] + atleta['nota_fisico'] + atleta['nota_finalizacao']) / 4)
                        
                        col_ovr, col_stats = st.columns([1, 2])
                        with col_ovr:
                            # Visual de Cartinha
                            st.markdown(f"<h1 style='text-align: center; color: #4CAF50; margin:0;'>{overall}</h1>", unsafe_allow_html=True)
                            st.markdown("<p style='text-align: center; font-weight: bold; margin:0;'>RATING</p>", unsafe_allow_html=True)
                        with col_stats:
                            st.markdown(f"⚡ **Ritmo (PAC):** {atleta['nota_velocidade']} | 🎯 **Passe (PAS):** {atleta['nota_passe']}")
                            st.markdown(f"💪 **Físico (FIS):** {atleta['nota_fisico']} | 🔥 **Chute (FIN):** {atleta['nota_finalizacao']}")
                            st.markdown(f"🏆 **Gols na Temporada:** {atleta['gols_marcados']}")
                        
                        st.markdown("---")
                        
                        # Rodapé do Post (Interações de curtidas sociais)
                        col_like, col_comment, _ = st.columns([1.5, 2, 5])
                        with col_like:
                            st.button(f"❤️ Curtir ({overall + 12})", key=f"like_atleta_{atleta['id_atleta']}")
                        with col_comment:
                            st.button("💬 Ver Scout", key=f"scout_atleta_{atleta['id_atleta']}")
                            
                    st.markdown("<br>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Adicione dados no banco para ver o feed: {e}")
            
    with aba_cadastro:
        st.subheader("📝 Cadastrar Novo Atleta na Rede")
        # (O seu formulário original continua aqui intacto e funcional)
        with st.form("form_atleta", clear_on_submit=True):
            nome = st.text_input("Nome Completo:")
            email = st.text_input("E-mail para Login:")
            senha = st.text_input("Senha de Acesso:", type="password")
            data_nasc = st.date_input("Data de Nascimento:", min_value=datetime(1990, 1, 1))
            posicao = st.selectbox("Posição Principal:", ['goleiro', 'zagueiro', 'lateral direito', 'lateral esquerdo', 'primeiro volante', 'segundo volante', 'meio campo', 'ponta esquerda', 'ponta direita', 'centro avante'])
            perna = st.selectbox("Pé Dominante:", ['destro', 'canhoto', 'ambidestro'])
            altura = st.number_input("Altura (em CM):", min_value=100, max_value=250, value=170)
            peso = st.number_input("Peso (em KG):", min_value=30.0, max_value=150.0, value=65.0, step=0.1)
            cidade = st.text_input("Cidade:")
            estado = st.text_input("Estado (Sigla):", max_chars=2).upper()
            autorizacao = st.selectbox("Autorização dos Pais:", ['Não se aplica', 'Sim', 'Não'])
            botao_atleta = st.form_submit_button("Criar Perfil Social")
            
            if botao_atleta and nome and email and senha and cidade and estado:
                try:
                    conn = criar_conexao()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id_atleta FROM atletas WHERE email = %s", (email,))
                    if cursor.fetchone():
                        st.error("⚠️ Este e-mail já existe!")
                    else:
                        senha_segura = criptografar_senha(senha)
                        query_atleta = "INSERT INTO atletas (nome, email, senha, data_nascimento, posicao_principal, perna_preferida, altura_cm, peso_kg, cidade, estado, autorizacao_pais) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(query_atleta, (nome, email, senha_segura, data_nasc, posicao, perna, altura, peso, cidade, estado, autorizacao))
                        id_novo_atleta = cursor.lastrowid
                        cursor.execute("INSERT INTO historico_desempenho (id_atleta, periodo, nota_velocidade, nota_passe, nota_fisico, nota_finalizacao, gols_marcados) VALUES (%s, 'Temporada Inicial', 60, 60, 60, 60, 0)", (id_novo_atleta,))
                        conn.commit()
                        st.success(f"Perfil de @{nome.lower().replace(' ', '_')} criado!")
                        st.balloons()
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"Erro: {e}")

# -----------------------------------------------------------------
# 🍻 COMUNIDADE PELADEIRO (Mural estilo feed de convites)
# -----------------------------------------------------------------
elif menu == "🍻 Comunidade Peladeiro":
    st.title("🍻 Central da Resenha & Peladas")
    aba_feed_jogos, aba_cadastro_p = st.tabs(["🏟️ Feed de Partidas", "📝 Criar Meu Perfil"])
    
    with aba_feed_jogos:
        st.subheader("Mural Interativo de Vagas")
        try:
            conn = criar_conexao()
            query_partidas = """
                SELECT p.id_partida, p.data_partida, p.horario, p.vagas_totais, p.vagas_confirmadas, q.nome_fantasia, q.cidade
                FROM partidas p
                INNER JOIN parceiros q ON p.id_parceiro = q.id_parceiro
                WHERE p.status_partida = 'Aberto'
            """
            df_partidas = pd.read_sql(query_partidas, conn)
            conn.close()
            
            if df_partidas.empty:
                st.info("Nenhuma quadra postou vagas para hoje ainda.")
            else:
                for index, partida in df_partidas.iterrows():
                    # CARD DE POST DE EVENTO (Estilo Redes Sociais)
                    with st.container(border=True):
                        c_img, c_detalhes = st.columns([1, 4])
                        with c_img:
                            st.image("https://cdn-icons-png.flaticon.com/512/5323/5323871.png", width=50)
                        with c_detalhes:
                            st.markdown(f"**📍 {partida['nome_fantasia']}** postou uma nova pelada!")
                            st.caption(f"Cidade: {partida['cidade']} | Horário: {partida['horario']} | Data: {partida['data_partida']}")
                        
                        vagas_restantes = partida['vagas_totais'] - partida['vagas_confirmadas']
                        
                        # Mensagem interativa do feed
                        st.info(f"🔥 **Faltam só {vagas_restantes} jogadores** para fechar o quórum dessa pelada! Bora?")
                        
                        c_b1, c_b2 = st.columns(2)
                        with c_b1:
                            if st.button("✅ Confirmar Presença", key=f"p_conf_{partida['id_partida']}", use_container_width=True):
                                conn = criar_conexao()
                                cursor = conn.cursor()
                                cursor.execute("UPDATE partidas SET vagas_confirmadas = vagas_confirmadas + 1 WHERE id_partida = %s", (partida['id_partida'],))
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success("Presença garantida no racha!")
                                st.rerun()
                        with c_b2:
                            st.button(f"📣 Convidar Amigos ({partida['vagas_confirmadas']})", key=f"p_share_{partida['id_partida']}", use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar feed: {e}")
            
    with aba_cadastro_p:
        st.subheader("📝 Cadastre-se para a Pelada")
        with st.form("form_peladeiro", clear_on_submit=True):
            nome = st.text_input("Nome ou Apelido:")
            email = st.text_input("E-mail:")
            senha = st.text_input("Senha:", type="password")
            idade = st.number_input("Idade:", min_value=5, max_value=100, value=20)
            cpf = st.text_input("CPF:")
            telefone = st.text_input("WhatsApp de Contato:")
            cidade = st.text_input("Cidade onde joga:")
            estado = st.text_input("Estado:", max_chars=2).upper()
            botao_peladeiro = st.form_submit_button("Entrar para a Comunidade")
            
            if botao_peladeiro and nome and email and senha:
                try:
                    conn = criar_conexao()
                    cursor = conn.cursor()
                    senha_segura = criptografar_senha(senha)
                    query = "INSERT INTO peladeiros (nome, email, senha, idade, cpf, telefone, city, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(query, (nome, email, senha_segura, idade, cpf, telefone, cidade, estado))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"Bem-vindo à resenha, {nome}!")
                except Exception as e:
                    st.error(f"Erro: {e}")

# -----------------------------------------------------------------
# 🏢 PARCEIROS & QUADRAS
# -----------------------------------------------------------------
elif menu == "🏢 Parceiros & Quadras":
    st.title("🏢 Quadras, Escolinhas e Clubes Parceiros")
    aba_parceiros = st.tabs(["🔎 Buscar Locais e Quadras", "🔐 Área Logada do Parceiro", "📝 Cadastrar Estabelecimento"])
    
    with aba_parceiros[0]:
        st.subheader("🗺️ Encontre a Quadra Perfeita")
        try:
            conn = criar_conexao()
            df_parc = pd.read_sql("SELECT nome_fantasia, tipo_parceiro, cidade, estado, telefone_comercial, preco_hora FROM parceiros", conn)
            conn.close()
            
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                cidades_disponiveis = ["Todas"] + list(df_parc['cidade'].unique())
                filtro_cidade = st.selectbox("Escolha a Cidade:", cidades_disponiveis)
            with f_col2:
                preco_max = st.slider("Preço Máximo da Hora (R$):", min_value=0, max_value=300, value=250, step=10)
            
            if filtro_cidade != "Todas":
                df_parc = df_parc[df_parc['cidade'] == filtro_cidade]
            df_parc = df_parc[df_parc['preco_hora'] <= preco_max]
            
            st.markdown("---")
            for index, local in df_parc.iterrows():
                with st.container(border=True):
                    l_info, l_preco = st.columns([3, 1])
                    with l_info:
                        st.markdown(f"### 🏟️ {local['nome_fantasia']}")
                        st.caption(f"🔹 Categoria: {local['tipo_parceiro'].title()} | 📍 {local['cidade']} - {local['estado']}")
                        st.text(f"📞 Contato: {local['telefone_comercial']}")
                    with l_preco:
                        st.metric("Preço/Hora", f"R$ {local['preco_hora']:.2f}")
        except Exception as e:
            st.error(f"Erro: {e}")
            
    with aba_parceiros[1]:
        st.subheader("🔐 Login do Parceiro")
        p_email = st.text_input("E-mail do Parceiro:", key="p_email")
        p_senha = st.text_input("Senha do Parceiro:", type="password", key="p_senha")
        
        if st.button("Entrar no Painel do Estabelecimento") or st.session_state.get("parceiro_logado", False):
            try:
                conn = criar_conexao()
                cursor = conn.cursor()
                cursor.execute("SELECT id_parceiro, nome_fantasia, tipo_parceiro, senha FROM parceiros WHERE email = %s", (p_email,))
                parc_res = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if parc_res and (verificar_senha(p_senha, parc_res[3]) or st.session_state.get("parceiro_logado", False)):
                    if not st.session_state.get("parceiro_logado", False):
                        st.session_state["parceiro_logado"] = True
                        st.session_state["id_parceiro_logado"] = parc_res[0]
                        st.session_state["nome_parceiro_logado"] = parc_res[1]
                        st.session_state["tipo_parceiro_logado"] = parc_res[2]
                    
                    st.success(f"Logado como: {st.session_state['nome_parceiro_logado']}")
                    
                    with st.sidebar.expander("💳 Status da Assinatura", expanded=True):
                        st.markdown("Plano: **NextDraft PRO**")
                        st.markdown("Status: 🟢 **Ativo**")
                    
                    if st.session_state["tipo_parceiro_logado"] == 'quadra':
                        st.subheader("🏟️ Abrir Nova Pelada Pública")
                        with st.form("form_abrir_pelada"):
                            d_partida = st.date_input("Data do Jogo:")
                            h_partida = st.text_input("Horário:", value="19:00")
                            v_vagas = st.number_input("Vagas Disponíveis:", min_value=2, max_value=30, value=14)
                            
                            if st.form_submit_button("Publicar Pelada no Mural"):
                                conn = criar_conexao()
                                cursor = conn.cursor()
                                cursor.execute("INSERT INTO partidas (id_parceiro, data_partida, horario, vagas_totais, vagas_confirmadas) VALUES (%s, %s, %s, %s, 0)", (st.session_state["id_parceiro_logado"], d_partida, h_partida, v_vagas))
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success("Partida lançada com sucesso no mural!")
                else:
                    st.error("Credenciais incorretas.")
            except Exception as e:
                st.error(f"Erro: {e}")
                
    with aba_parceiros[2]:
        st.subheader("📝 Cadastre seu Negócio ou Clube")
        with st.form("form_parceiro", clear_on_submit=True):
            nome_fantasia = st.text_input("Nome da Quadra ou Clube:")
            email = st.text_input("E-mail Comercial:")
            senha = st.text_input("Senha:")
            cnpj = st.text_input("CNPJ:")
            tipo = st.selectbox("Tipo:", ['quadra', 'escolinha', 'clube'])
            tel = st.text_input("Telefone Comercial:")
            cidade = st.text_input("Cidade:")
            estado = st.text_input("Estado:", max_chars=2).upper()
            preco = st.number_input("Preço da Hora (R$):", min_value=0.0, value=120.0, step=10.0)
            botao_parceiro = st.form_submit_button("Cadastrar Parceiro")
            
            if botao_parceiro and nome_fantasia and email and senha:
                try:
                    conn = criar_conexao()
                    cursor = conn.cursor()
                    senha_segura = criptografar_senha(senha)
                    query = "INSERT INTO parceiros (nome_fantasia, email, senha, cnpj, tipo_parceiro, telefone_comercial, cidade, estado, preco_hora) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(query, (nome_fantasia, email, senha_segura, cnpj, tipo, tel, cidade, estado, preco))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"{nome_fantasia} adicionado com segurança!")
                except Exception as e:
                    st.error(f"Erro: {e}")

# -----------------------------------------------------------------
# 🔐 PAINEL ADMIN MASTER (Gráficos Gerais)
# -----------------------------------------------------------------
elif menu == "🔐 Painel Admin":
    st.title("🔐 Painel Administrativo & Analytics")
    
    admin_email = st.text_input("E-mail do Administrador:", key="admin_email_input")
    admin_senha = st.text_input("Senha Secreta:", type="password", key="admin_senha_input")
    
    if st.button("Entrar no Painel Master") or st.session_state.get("admin_logado", False):
        try:
            if (admin_email == os.getenv("ADMIN_USER") and admin_senha == os.getenv("ADMIN_PASS")) or st.session_state.get("admin_logado", False):
                st.session_state["admin_logado"] = True
                st.success("Acesso Autorizado! Carregando Analytics...")
                st.markdown("---")
                
                conn = criar_conexao()
                total_atletas = pd.read_sql("SELECT COUNT(*) AS total FROM atletas", conn)['total'][0]
                total_peladeiros = pd.read_sql("SELECT COUNT(*) AS total FROM peladeiros", conn)['total'][0]
                total_parceiros = pd.read_sql("SELECT COUNT(*) AS total FROM parceiros", conn)['total'][0]
                faturamento_quadras = pd.read_sql("SELECT SUM(preco_hora) AS total FROM parceiros WHERE tipo_parceiro='quadra'", conn)['total'][0] or 0.0
                df_posicoes = pd.read_sql("SELECT posicao_principal, COUNT(*) as quantidade FROM atletas GROUP BY posicao_principal", conn)
                conn.close()
                
                m1, m2 = st.columns(2)
                m1.metric("🏃 Atletas Base", total_atletas)
                m2.metric("🍻 Peladeiros", total_peladeiros)
                
                m3, m4 = st.columns(2)
                m3.metric("🏢 Parceiros", total_parceiros)
                m4.metric("💰 Potencial Quadras", f"R$ {faturamento_quadras:.2f}")
                
                st.markdown("### 📊 Inteligência de Mercado (Scouting)")
                
                if not df_posicoes.empty:
                    df_posicoes['posicao_principal'] = df_posicoes['posicao_principal'].str.title()
                    fig = px.bar(
                        df_posicoes, 
                        x='quantidade', 
                        y='posicao_principal', 
                        orientation='h',
                        title="Distribuição de Atletas por Posição",
                        labels={'quantidade': 'Nº de Jogadores', 'posicao_principal': 'Posição'},
                        color='quantidade',
                        color_continuous_scale='Greens'
                    )
                    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False, height=350)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Credenciais administrativas inválidas.")
        except Exception as e:
            st.error(f"Erro no painel: {e}")