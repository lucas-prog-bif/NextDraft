import streamlit as st
import mysql.connector
import pandas as pd
import dotenv
import os
import hashlib
from datetime import datetime

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

# Configuração inicial da página
st.set_page_config(page_title="NextDraft Ecosystem", page_icon="⚽", layout="wide")

# 🔄 GERENCIADOR DE ESTADO (Navegação instantânea)
if "navegacao_radio" not in st.session_state:
    st.session_state["navegacao_radio"] = "🏠 Início"

def ir_para_cadastro_atleta():
    st.session_state["navegacao_radio"] = "🏃 Área do Atleta"

def ir_para_cadastro_peladeiro():
    st.session_state["navegacao_radio"] = "🍻 Comunidade Peladeiro"

def ir_para_cadastro_parceiro():
    st.session_state["navegacao_radio"] = "🏢 Parceiros & Quadras"

# 2. MENU LATERAL DE NAVEGAÇÃO
st.sidebar.title("⚽ NextDraft v2")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegue pelo App:",
    ["🏠 Início", "🏃 Área do Atleta", "🍻 Comunidade Peladeiro", "🏢 Parceiros & Quadras", "🔐 Painel Admin"],
    key="navegacao_radio"
)

# -----------------------------------------------------------------
# 🏠 TELA INICIAL
# -----------------------------------------------------------------
if menu == "🏠 Início":
    st.title("Bem-vindo ao NextDraft")
    st.subheader("Conectando o futebol da base à várzea através dos dados.")
    st.write("Escolha o seu perfil abaixo para simular as jornadas e cadastros do ecossistema.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🏃 Atletas de Base")
        st.write("Crie o seu perfil técnico de monitoramento, exiba suas notas estilo FIFA e fique visível para escolinhas e clubes.")
        st.button("🚀 Ir para Área de Atletas", on_click=ir_para_cadastro_atleta, use_container_width=True)
    with col2:
        st.markdown("### 🍻 Peladeiros da Várzea")
        st.write("Encontre jogos perto de você, confirme presença para fechar o quórum e ganhe notas de resenha da galera.")
        st.button("⚽ Entrar para a Comunidade", on_click=ir_para_cadastro_peladeiro, use_container_width=True)
    with col3:
        st.markdown("### 🏢 Quadras e Escolinhas")
        st.write("Divulgue seus horários de locação, gerencie mensalidades e use dados de evolução técnica com seus alunos.")
        st.button("🏢 Registrar Estabelecimento", on_click=ir_para_cadastro_parceiro, use_container_width=True)

# -----------------------------------------------------------------
# 🏃 ÁREA DO ATLETA (Cartinhas FIFA e Inscrição)
# -----------------------------------------------------------------
elif menu == "🏃 Área do Atleta":
    st.title("🏃 Painel de Atletas de Alto Rendimento")
    aba_atleta = st.tabs(["🔎 Buscar Atletas", "📝 Cadastrar Novo Atleta"])
    
    with aba_atleta[0]:
        st.subheader("📋 Cartões de Monitoramento (Estilo FIFA)")
        try:
            conn = criar_conexao()
            query = """
                SELECT a.id_atleta, a.nome, a.posicao_principal, a.perna_preferida, a.altura_cm, a.peso_kg, a.cidade, a.estado,
                       h.nota_velocidade, h.nota_passe, h.nota_fisico, h.nota_finalizacao, h.gols_marcados, p.nome_fantasia as escolinha
                FROM atletas a
                INNER JOIN historico_desempenho h ON a.id_atleta = h.id_atleta
                LEFT JOIN parceiros p ON a.id_parceiro_treinador = p.id_parceiro
            """
            df = pd.read_sql(query, conn)
            conn.close()
            
            todas_posicoes = ["Todos"] + list(df['posicao_principal'].unique())
            filtro_posicao = st.selectbox("Filtrar por Posição:", todas_posicoes)
            if filtro_posicao != "Todos":
                df = df[df['posicao_principal'] == filtro_posicao]
            
            st.markdown("---")
            for index, atleta in df.iterrows():
                with st.container(border=True):
                    c_info, c_notas, c_estatisticas = st.columns([2, 2, 1])
                    with c_info:
                        st.markdown(f"### 👤 {atleta['nome']}")
                        escolinha_nome = atleta['escolinha'] if atleta['escolinha'] else "Sem Clube/Escolinha"
                        st.caption(f"🛡️ Clube: **{escolinha_nome}** | 📍 {atleta['cidade']} - {atleta['estado']}")
                        st.markdown(f"**Posição:** `{atleta['posicao_principal'].title()}`")
                        st.markdown(f"**Pé Dominante:** {atleta['perna_preferida'].title()}")
                        st.text(f"📏 {atleta['altura_cm']} cm | ⚖️ {atleta['peso_kg']} kg")
                    with c_notas:
                        st.markdown("**📊 Atributos Técnicos**")
                        n1, n2 = st.columns(2)
                        n1.metric("⚡ PAC (Velocidade)", atleta['nota_velocidade'])
                        n2.metric("🎯 PAS (Passe)", atleta['nota_passe'])
                        n3, n4 = st.columns(2)
                        n3.metric("💪 FIS (Físico)", atleta['nota_fisico'])
                        n4.metric("⚽ FIN (Finalização)", atleta['nota_finalizacao'])
                    with c_estatisticas:
                        st.markdown("**🏆 Temporada**")
                        overall = int((atleta['nota_velocidade'] + atleta['nota_passe'] + atleta['nota_fisico'] + atleta['nota_finalizacao']) / 4)
                        st.metric("⭐️ OVERALL", overall)
                        st.metric("🔥 Gols", atleta['gols_marcados'])
                st.markdown("<br>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar atletas: {e}")
            
    with aba_atleta[1]:
        st.subheader("📝 Formulário de Inscrição do Atleta")
        try:
            conn = criar_conexao()
            escolinhas_df = pd.read_sql("SELECT id_parceiro, nome_fantasia FROM parceiros WHERE tipo_parceiro='escolinha' OR tipo_parceiro='clube'", conn)
            conn.close()
        except:
            escolinhas_df = pd.DataFrame()

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
            estado = st.text_input("Estado (Sigla, ex: SP):", max_chars=2).upper()
            
            if not escolinhas_df.empty:
                opcoes_esc = {"Nenhuma / Atleta Livre": None}
                for i, r in escolinhas_df.iterrows():
                    opcoes_esc[r['nome_fantasia']] = r['id_parceiro']
                escolinha_sel = st.selectbox("Vincular à Escolinha/Clube de Treino:", list(opcoes_esc.keys()))
                id_esc_final = opcoes_esc[escolinha_sel]
            else:
                id_esc_final = None

            autorizacao = st.selectbox("Autorização dos Pais:", ['Não se aplica', 'Sim', 'Não'])
            botao_atleta = st.form_submit_button("Salvar Cadastro do Atleta")
            
            if botao_atleta and nome and email and senha and cidade and estado:
                try:
                    conn = criar_conexao()
                    cursor = conn.cursor()
                    # CRIPTOGRAFIA ATIVADA NO CADASTRO:
                    senha_segura = criptografar_senha(senha)
                    query_atleta = "INSERT INTO atletas (nome, email, senha, data_nascimento, posicao_principal, perna_preferida, altura_cm, peso_kg, cidade, estado, autorizacao_pais, id_parceiro_treinador) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" if 'city' in pd.read_sql("DESCRIBE atletas", conn)['Field'].values else "INSERT INTO atletas (nome, email, senha, data_nascimento, posicao_principal, perna_preferida, altura_cm, peso_kg, cidade, estado, autorizacao_pais, id_parceiro_treinador) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    
                    cursor.execute(query_atleta, (nome, email, senha_segura, data_nasc, posicao, perna, altura, peso, cidade, estado, autorizacao, id_esc_final))
                    id_novo_atleta = cursor.lastrowid
                    query_hist = "INSERT INTO historico_desempenho (id_atleta, periodo, nota_velocidade, nota_passe, nota_fisico, nota_finalizacao) VALUES (%s, 'Temporada Inicial', 60, 60, 60, 60)"
                    cursor.execute(query_hist, (id_novo_atleta,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"Atleta {nome} cadastrado com segurança!")
                except Exception as e:
                    st.error(f"Erro: {e}")

# -----------------------------------------------------------------
# 🍻 COMUNIDADE PELADEIRO (Confirmação de Presença)
# -----------------------------------------------------------------
elif menu == "🍻 Comunidade Peladeiro":
    st.title("🍻 Espaço do Peladeiro & Resenha")
    aba_peladeiro = st.tabs(["🔎 Buscar Peladas e Jogos", "📝 Cadastrar Novo Peladeiro"])
    
    with aba_peladeiro[0]:
        st.subheader("⚽ Jogos e Peladas Precisando de Jogador")
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
                st.info("Nenhuma pelada com vagas aberta na sua região hoje.")
            else:
                for index, partida in df_partidas.iterrows():
                    with st.container(border=True):
                        col_j1, col_j2, col_j3 = st.columns([2, 1, 1])
                        with col_j1:
                            st.markdown(f"### 🏟️ Pelada na {partida['nome_fantasia']}")
                            st.caption(f"📍 Cidade: {partida['cidade']} | ⏰ Horário: {partida['horario']} | Data: {partida['data_partida']}")
                        with col_j2:
                            vagas_restantes = partida['vagas_totais'] - partida['vagas_confirmadas']
                            st.metric("Vagas Restantes", f"{vagas_restantes} livres", delta=f"{partida['vagas_confirmadas']} confirmados")
                        with col_j3:
                            st.write("")
                            if st.button("Confirmar Minha Presença", key=f"partida_{partida['id_partida']}"):
                                conn = criar_conexao()
                                cursor = conn.cursor()
                                cursor.execute("UPDATE partidas SET vagas_confirmadas = vagas_confirmadas + 1 WHERE id_partida = %s", (partida['id_partida'],))
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success("Presença confirmada!")
                                st.rerun()
        except Exception as e:
            st.error(f"Erro ao carregar partidas: {e}")
            
    with aba_peladeiro[1]:
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
                    # CRIPTOGRAFIA NA CRIAÇÃO DO PELADEIRO:
                    senha_segura = criptografar_senha(senha)
                    query = "INSERT INTO peladeiros (nome, email, senha, idade, cpf, telefone, cidade, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(query, (nome, email, senha_segura, idade, cpf, telefone, cidade, estado))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"Bem-vindo à resenha, {nome}!")
                except Exception as e:
                    st.error(f"Erro: {e}")

# -----------------------------------------------------------------
# 🏢 PARCEIROS & QUADRAS (Comunicação Financeira / Mensalidades)
# -----------------------------------------------------------------
elif menu == "🏢 Parceiros & Quadras":
    st.title("🏢 Quadras, Escolinhas e Clubes Parceiros")
    aba_parceiros = st.tabs(["🔎 Buscar Locais e Quadras", "🔐 Área Logada do Parceiro", "📝 Cadastrar Estabelecimento"])
    
    with aba_parceiros[0]:
        st.subheader("🗺️ Encontre a Quadra Perfeita para o seu Jogo")
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
                        st.text(f"📞 Contato Comercial: {local['telefone_comercial']}")
                    with l_preco:
                        st.metric("Preço/Hora", f"R$ {local['preco_hora']:.2f}")
        except Exception as e:
            st.error(f"Erro: {e}")
            
    with aba_parceiros[1]:
        st.subheader("🔐 Login do Parceiro (Escolinhas / Quadras)")
        p_email = st.text_input("E-mail do Parceiro:", key="p_email")
        p_senha = st.text_input("Senha do Parceiro:", type="password", key="p_senha")
        
        if st.button("Entrar no Painel do Estabelecimento") or st.session_state.get("parceiro_logado", False):
            try:
                conn = criar_conexao()
                cursor = conn.cursor()
                # Puxa o hash da senha cadastrada
                cursor.execute("SELECT id_parceiro, nome_fantasia, tipo_parceiro, senha FROM parceiros WHERE email = %s", (p_email,))
                parc_res = cursor.fetchone()
                cursor.close()
                conn.close()
                
                # VERIFICAÇÃO CRIPTOGRÁFICA DE SENHA PARA ENTRAR
                if parc_res and (verificar_senha(p_senha, parc_res[3]) or st.session_state.get("parceiro_logado", False)):
                    if not st.session_state.get("parceiro_logado", False):
                        st.session_state["parceiro_logado"] = True
                        st.session_state["id_parceiro_logado"] = parc_res[0]
                        st.session_state["nome_parceiro_logado"] = parc_res[1]
                        st.session_state["tipo_parceiro_logado"] = parc_res[2]
                    
                    # 💸 OPÇÃO DE NEGÓCIO 2: INTERFACE FINANCEIRA SIMULADA
                    st.success(f"Logado com sucesso: {st.session_state['nome_parceiro_logado']}")
                    
                    with st.sidebar.expander("💳 Status da Minha Assinatura", expanded=True):
                        st.markdown("Plano: **NextDraft PRO**")
                        st.markdown("Status: 🟢 **Adimplente / Ativo**")
                        st.markdown("Próxima fatura: **05/07/2026**")
                        st.caption("Mensalidade: R$ 59,90/mês")
                    
                    st.markdown("---")
                    
                    if st.session_state["tipo_parceiro_logado"] in ['escolinha', 'clube']:
                        st.subheader("📋 Avaliar Meus Alunos Cadastrados")
                        conn = criar_conexao()
                        meus_alunos = pd.read_sql("SELECT id_atleta, nome FROM atletas WHERE id_parceiro_treinador = %s", conn, params=[st.session_state["id_parceiro_logado"]])
                        conn.close()
                        
                        if meus_alunos.empty:
                            st.info("Nenhum atleta vinculado à sua escolinha ainda.")
                        else:
                            aluno_sel = st.selectbox("Selecione o Aluno para Dar Notas:", meus_alunos['nome'].unique())
                            id_aluno_sel = int(meus_alunos[meus_alunos['nome'] == aluno_sel]['id_atleta'].values[0])
                            
                            with st.form("form_notas_treinador"):
                                v_pac = st.slider("Velocidade (PAC):", 1, 99, 70, key="tpac")
                                v_pas = st.slider("Passe (PAS):", 1, 99, 70, key="tpas")
                                v_fis = st.slider("Físico (FIS):", 1, 99, 70, key="tfis")
                                v_fin = st.slider("Finalização (FIN):", 1, 99, 70, key="tfin")
                                v_gols = st.number_input("Gols do Aluno:", min_value=0, value=0, key="tgols")
                                
                                if st.form_submit_button("Salvar Avaliação do Professor"):
                                    conn = criar_conexao()
                                    cursor = conn.cursor()
                                    cursor.execute("UPDATE historico_desempenho SET nota_velocidade=%s, nota_passe=%s, nota_fisico=%s, nota_finalizacao=%s, gols_marcados=%s WHERE id_atleta=%s", (v_pac, v_pas, v_fis, v_fin, v_gols, id_aluno_sel))
                                    conn.commit()
                                    cursor.close()
                                    conn.close()
                                    st.success(f"Notas salvas pelo treinador!")
                    
                    elif st.session_state["tipo_parceiro_logado"] == 'quadra':
                        st.subheader("🏟️ Abrir Nova Pelada Pública (Captar Clientes)")
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
                    st.error("Credenciais de parceiro incorretas.")
            except Exception as e:
                st.error(f"Erro no painel do parceiro: {e}")
            
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
                    # CRIPTOGRAFIA NA CRIAÇÃO DO PARCEIRO:
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
# 🔐 PAINEL ADMIN MASTER (Métricas Gerais e Login Seguro)
# -----------------------------------------------------------------
elif menu == "🔐 Painel Admin":
    st.title("🔐 Login de Administrador Geral")
    admin_email = st.text_input("E-mail do Administrador:")
    admin_senha = st.text_input("Senha Secreta:", type="password")
    
    if st.button("Entrar no Panel Master") or st.session_state.get("admin_logado", False):
        try:
            conn = criar_conexao()
            cursor = conn.cursor()
            cursor.execute("SELECT senha, nome_admin FROM usuarios WHERE email = %s", (admin_email,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            
            # VERIFICAÇÃO CRIPTOGRÁFICA DO ADMIN
            if resultado and (verificar_senha(admin_senha, resultado[0]) or st.session_state.get("admin_logado", False)):
                st.session_state["admin_logado"] = True
                st.success(f"Acessado como: Administrador Geral")
                st.markdown("---")
                
                conn = criar_conexao()
                total_atletas = pd.read_sql("SELECT COUNT(*) AS total FROM atletas", conn)['total'][0]
                total_peladeiros = pd.read_sql("SELECT COUNT(*) AS total FROM peladeiros", conn)['total'][0]
                total_parceiros = pd.read_sql("SELECT COUNT(*) AS total FROM parceiros", conn)['total'][0]
                faturamento_quadras = pd.read_sql("SELECT SUM(preco_hora) AS total FROM parceiros WHERE tipo_parceiro='quadra'", conn)['total'][0]
                conn.close()
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Atletas Cadastrados", total_atletas)
                m2.metric("Peladeiros Ativos", total_peladeiros)
                m3.metric("Parceiros Totais", total_parceiros)
                m4.metric("Potencial de Quadras", f"R$ {faturamento_quadras or 0.0:.2f}")
            else:
                st.error("Acesso Negado.")
        except Exception as e:
            st.error(f"Erro: {e}")