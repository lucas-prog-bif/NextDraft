# EXTENSOES E BIBLIOTECAS QUE TIVE QUE INSTALAR DENTRO DO TERMINAL
import streamlit as st
import pandas as pd
import mysql.connector
import time
import os
import re
import base64
from PIL import Image
import io
import datetime as dt_modulo
from datetime import datetime, timedelta, date
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor

# 1. CONFIGURAÇÃO DA PÁGINA (APENAS UMA VEZ E NO TOPO!)
# ==========================================
st.set_page_config(
    page_title="NextDraft", 
    page_icon="⚽", 
    layout="wide", 
    initial_sidebar_state="expanded" # linha da barra lateral
)
# ==========================================


# 2. INICIALIZAÇÃO SEGURA DO ESTADO DA SESSÃO
# ==========================================
if "logado" not in st.session_state: st.session_state["logado"] = False
if "usuario_id" not in st.session_state: st.session_state["usuario_id"] = None
if "usuario_nome" not in st.session_state: st.session_state["usuario_nome"] = ""
if "usuario_perfil" not in st.session_state: st.session_state["usuario_perfil"] = ""
if "story_aberto" not in st.session_state: st.session_state["story_aberto"] = None
# ==========================================

st.markdown(
    """
    <style>
        input, select, textarea { font-size: 16px !important; }
        
        @media screen and (-webkit-min-device-pixel-ratio:0) { 
            select, textarea, input { font-size: 16px !important; }
        }

        [data-testid="stAppViewContainer"] {
            width: 100% !important;
        }
        
        [data-testid="stMainBlockContainer"] {
            max-width: 100% !important;
        }

        /* ==========================================
           ⚽ FORÇANDO A PALAVRA "MENU" NO CABEÇALHO
           ========================================== */
        
        /* Aplica o estilo de botão verde em todos os botões do cabeçalho */
        header[data-testid="stHeader"] button {
            background-color: #2e7d32 !important; /* Fundo verde futebol */
            border-radius: 6px !important;
            padding: 4px 10px !important;
            width: auto !important;
            height: auto !important;
        }

        /* Esconde o desenho original das setinhas e dos três pontinhos */
        header[data-testid="stHeader"] button svg {
            display: none !important;
        }

        /* Injeta o texto MENU em letras garrafais */
        header[data-testid="stHeader"] button::after {
            content: "☰ MENU" !important;
            color: #ffffff !important;
            font-size: 13px !important;
            font-weight: bold !important;
            font-family: Arial, sans-serif !important;
        }

        /* ==========================================
           🚨 BOTÃO DE CONTATO EM VERMELHO
           ========================================== */
        
        /* Encontra o botão gerado pelo st.link_button no Streamlit */
        a[data-testid="stBaseButton-link"] {
            background-color: #d32f2f !important; /* Vermelho esportivo */
            color: white !important;               /* Texto branco */
            border: none !important;
            font-weight: bold !important;
            border-radius: 4px !important;
            transition: 0.2s !important;
        }

        /* Efeito de clique no celular */
        a[data-testid="stBaseButton-link"]:hover {
            background-color: #9a0007 !important; /* Vermelho mais escuro */
        }
    </style>
    """,
    unsafe_allow_html=True
)



# 3. FUNÇÕES UTILITÁRIAS
# ==========================================
def criar_conexao():
    # Agora estamos buscando as chaves que você configurou no Streamlit
    host = st.secrets["DB_HOST"]
    user = st.secrets["DB_USER"]
    password = st.secrets["DB_PASSWORD"]
    database = st.secrets["DB_NAME"]
    
    # Monte a string de conexão usando essas variáveis
    db_url = st.secrets["DATABASE_URL"]
    conn = psycopg2.connect(db_url, sslmode='require')
    return conn
    # ... resto do seu código de conexão

def executar_consulta(sql):
    conn = criar_conexao() # A função que você já tem
    
    # É AQUI que você coloca a linha:
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute(sql)
    resultados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return resultados

DB_URL = st.secrets["DATABASE_URL"]


def recriar_estrutura():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # Coloque aqui os comandos CREATE TABLE que funcionam no Postgres
    # (Você pode pegar os do seu arquivo .sql e apenas ajustar tipos como 'INT' para 'INTEGER')
    comandos_sql = """
    CREATE TABLE  IF NOT EXISTS usuarios (
    id_usuario serial PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo_perfil VARCHAR(20) NOT NULL, -- 'atleta', 'peladeiro', 'quadra', 'admin'
    subtitulo_autor VARCHAR(100),
    url_avatar varchar (255) not null,
    biografia text not null,
    posicao varchar (50),
    time_coracao varchar (100),
    foto_perfil text,
    vel integer,
    pas integer,
    fin integer,
    dri integer,
    def integer,
    fis integer,
    status_conta varchar (20),
    data_expiracao date,
    status_pagamento varchar (20)
    
);

CREATE TABLE IF NOT EXISTS stories_parceiros (
    id SERIAL PRIMARY KEY,
    nome_parceiro VARCHAR(100) NOT NULL,
    url_logo VARCHAR(255),
    imagem_story VARCHAR(255),
    texto_story TEXT,
    link_cupom VARCHAR(255),
    data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_anuncio VARCHAR(20) DEFAULT 'ativo',
    data_vencimento DATE,
    tipo_plano VARCHAR(50),
    semanas_contratadas INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS solicitacoes_pagamento (
    id SERIAL PRIMARY KEY,
    id_usuario INTEGER,
    nome_usuario VARCHAR(100),
    caminho_comprovante VARCHAR(255),
    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pendente'
);
CREATE TABLE IF NOT EXISTS postagens_quadras (
    id_post SERIAL PRIMARY KEY,
    nome_arena VARCHAR(100) NOT NULL,
    conteudo TEXT NOT NULL,
    tag_promocao VARCHAR(50) DEFAULT 'Geral',
    data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_hora_jogo TIMESTAMP,
    id_pelada_vinculada INTEGER,
    data_jogo DATE,
    hora_jogo TIME,
    valor DECIMAL(10, 2),
    endereco_arena VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS postagens_clubes (
    id_post SERIAL PRIMARY KEY,
    nome_clube VARCHAR(100) NOT NULL,
    conteudo TEXT NOT NULL,
    tag_aviso VARCHAR(50) DEFAULT 'Geral',
    zap_contato VARCHAR(20),
    email_contato VARCHAR(100),
    data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nome_arquivo_media VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS peladas_ativas (
    id_pelada SERIAL PRIMARY KEY,
    nome_jogo VARCHAR(255) DEFAULT 'Partida',
    nome_arena VARCHAR(255) DEFAULT 'Não informada',
    endereco_arena VARCHAR(255) DEFAULT 'Não informado',
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_alfa INTEGER NOT NULL,
    nome_alfa VARCHAR(100) NOT NULL,
    max_linha_por_time INTEGER DEFAULT 5,
    valor_pix DECIMAL(10, 2) DEFAULT 0.00,
    chave_pix VARCHAR(100),
    status_jogo VARCHAR(20) DEFAULT 'Aberto'
);
CREATE TABLE IF NOT EXISTS peladas (
    id_pelada SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    dia_semana VARCHAR(20) NOT NULL,
    cidade VARCHAR(50) NOT NULL,
    bairro VARCHAR(50),
    horario TIME,
    descricao TEXT,
    status_pagamento VARCHAR(20) DEFAULT 'pendente',
    data_vencimento_mensalidade DATE
);
CREATE TABLE IF NOT EXISTS notificacoes (
    id_notificacao SERIAL PRIMARY KEY,
    id_usuario_destino INTEGER NOT NULL,
    mensagem VARCHAR(255) NOT NULL,
    tipo_alerta VARCHAR(50) DEFAULT 'info',
    lida BOOLEAN DEFAULT FALSE,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS mensagens_chat (
    id_mensagem SERIAL PRIMARY KEY,
    id_envia INTEGER NOT NULL,
    nome_envia VARCHAR(100) NOT NULL,
    id_recebe INTEGER DEFAULT 0,
    id_pelada INTEGER,
    mensagem TEXT NOT NULL,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS jogadores_pelada (
    id_inscricao SERIAL PRIMARY KEY,
    id_horario INTEGER NOT NULL,
    username_jogador VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS horarios_quadras (
    id_horario SERIAL PRIMARY KEY,
    nome_quadra VARCHAR(100) NOT NULL,
    data_hora_jogo TIMESTAMP NOT NULL,
    vagas_minimas INTEGER DEFAULT 10,
    status VARCHAR(20) DEFAULT 'disponivel',
    username_organizador VARCHAR(100)
);
CREATE TABLE IF NOT EXISTS habilidades_atletas (
    id_habilidade SERIAL PRIMARY KEY,
    id_atleta INTEGER NOT NULL,
    nota_velocidade INTEGER DEFAULT 60,
    nota_passe INTEGER DEFAULT 60,
    nota_fisico INTEGER DEFAULT 60,
    nota_finalizacao INTEGER DEFAULT 60,
    nota_defesa INTEGER DEFAULT 60,
    nota_drible INTEGER DEFAULT 60,
    gols_marcados INTEGER DEFAULT 0,
    assistencias INTEGER DEFAULT 0,
    partidas_jogadas INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS escalacao_pelada (
    id_escalacao SERIAL PRIMARY KEY,
    id_pelada INTEGER NOT NULL,
    id_jogador INTEGER NOT NULL,
    nome_jogador VARCHAR(100) NOT NULL,
    overall_jogador INTEGER DEFAULT 60,
    time_escalado VARCHAR(10) NOT NULL,
    posicao_quadra VARCHAR(20) NOT NULL,
    status_vaga VARCHAR(20) DEFAULT 'Pendente'
);
CREATE TABLE IF NOT EXISTS curtidas_posts (
    id_curtida SERIAL PRIMARY KEY,
    id_post INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS curtidas_comentarios (
    id_curtida SERIAL PRIMARY KEY,
    id_comentario INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS comentarios_posts (
    id_comentario SERIAL PRIMARY KEY,
    id_post INTEGER NOT NULL,
    username VARCHAR(50) NOT NULL,
    comentario TEXT NOT NULL,
    id_resposta INTEGER,
    curtidas INTEGER DEFAULT 0,
    fixado BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS comentarios (
    id_comentario SERIAL PRIMARY KEY,
    id_post INTEGER NOT NULL,
    username_autor VARCHAR(50) NOT NULL,
    texto TEXT NOT NULL,
    id_comentario_pai INTEGER,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS chat_peladas (
    id_mensagem SERIAL PRIMARY KEY,
    id_pelada INTEGER,
    id_usuario INTEGER,
    nome_usuario VARCHAR(255),
    mensagem TEXT,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS atletas (
    id_atleta SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_nascimento DATE,
    posicao_principal VARCHAR(50),
    perna_preferida VARCHAR(20),
    altura_cm INTEGER,
    peso_kg DECIMAL(5, 2),
    cidade VARCHAR(100),
    estado CHAR(2),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""

    cur.execute(comandos_sql)
    conn.commit()
    print("Tabelas criadas com sucesso na nuvem!")
    cur.close()
    conn.close()

recriar_estrutura()

def tem_permissao(nivel_requerido):
    perfil = st.session_state.get("usuario_perfil")
    if perfil == "ADMIN": return True 
    if isinstance(nivel_requerido, list): return perfil in nivel_requerido
    return perfil == nivel_requerido

def exibir_aba_quadras():

    
    # Resgatando dados do usuário ativo
    id_usuario_atual = int(st.session_state['usuario_id'])
    nome_usuario_atual = st.session_state.get('usuario_nome', 'Jogador')
    overall_usuario_atual = int(st.session_state.get('usuario_overall', 60))

    st.markdown("## 🏟️ Central das Quadras & Arenas")
    
    # --- CONFIGURAÇÃO DAS SUB-ABAS ---
    sub_aba1, sub_aba2 = st.tabs(["📢 Mural de Ofertas & Avisos", "✍️ Nova Postagem da Arena"])
    
    # Dados simulados do usuário logado (Certifique-se de que st.session_state["usuario_id"] e nome_usuario existem no seu app)
    id_usuario_atual = st.session_state.get("usuario_id", 0)
    nome_usuario_atual = st.session_state.get("usuario_nome", "Usuário Teste")
    # Tenta pegar o overall real, se não tiver, usa padrão 75 para o teste
    overall_usuario_atual = st.session_state.get("usuario_overall", 75) 
    
    # ==========================================================================
    # SUB-ABA 1: O FEED RECENTE DAS QUADRAS (O MURAL)
    # ==========================================================================
    with sub_aba1:
        st.markdown("### 📰 Ofertas e Horários Recentes")
        conn = criar_conexao()
        
        # Query garantida (usando p.id_post conforme sua tabela)
        query = """
            SELECT p.*, pa.nome_alfa, pa.id_alfa 
            FROM postagens_quadras p
            LEFT JOIN peladas_ativas pa ON p.id_pelada_vinculada = pa.id_pelada
            ORDER BY p.id_post DESC
        """
        df_posts = pd.read_sql(query, conn)
        
        if not df_posts.empty:
            for row in df_posts.itertuples():
                with st.container(border=True):
                    # Usamos getattr para evitar erros caso a coluna não exista ou seja None
                    nome_arena = getattr(row, 'nome_arena', 'Arena sem nome')
                    endereco = getattr(row, 'endereco_arena', 'Endereço não informado')
                    
                    st.markdown(f"#### **{nome_arena}**")
                    st.caption(f"📍 {endereco}")
                    
                    st.caption(f"📌 `{getattr(row, 'tag_promocao', 'Geral')}`")
                    st.markdown(getattr(row, 'conteudo', ''))
                    
                    # Exibir data e valor formatados
                    col_info1, col_info2 = st.columns(2)
                    # Verifica se valor é numérico antes de formatar
                    valor = float(row.valor) if row.valor is not None else 0.0
                    col_info1.info(f"📅 Dados: {row.data_jogo}")
                    col_info2.info(f"💵 Valor: R$ {valor:.2f}")
                    
                    # VERIFICAÇÃO DO ALFA
                    # Verifica se o campo não é NaN (nulo)
                    if not pd.isna(row.id_pelada_vinculada):
                        # Trata os valores None/NaN do JOIN
                        id_alfa = row.id_alfa if row.id_alfa is not None else 0
                        nome_alfa = row.nome_alfa if row.nome_alfa is not None else "Aguardando Organizador"
                        
                        if id_alfa == 0 or nome_alfa == "Aguardando Organizador":
                            if st.button("👑 Assumir como Boleiro Alfa", key=f"btn_{row.id_post}"):
                                cursor = conn.cursor()
                                # 1. Atualiza o Alfa
                                cursor.execute("UPDATE peladas_ativas SET nome_alfa = %s, id_alfa = %s WHERE id_pelada = %s", 
                                            (st.session_state["usuario_nome"], st.session_state["usuario_id"], row.id_pelada_vinculada))
                                
                                # 2. INSERE A MENSAGEM DE BOAS-VINDAS (Isso cria o chat no banco)
                                msg_boas_vindas = f"👑 O boleiro {st.session_state['usuario_nome']} assumiu a organização desta pelada!"
                                cursor.execute("""
                                    INSERT INTO mensagens_chat (id_envia, nome_envia, id_pelada, mensagem) 
                                    VALUES (0, 'Sistema', %s, %s)
                                """, (row.id_pelada_vinculada, msg_boas_vindas))
                                
                                conn.commit()
                                st.rerun()
                        else:
                            st.success(f"🏃‍♂️ Organizado por: {nome_alfa}")

    # ==========================================================================
    # SUB-ABA 2: FORMULÁRIO DE POSTAGEM DA ARENA (CRIAÇÃO COMPLETA CORRIGIDA)
    # ==========================================================================
    with sub_aba2:
        # 1. Verifica se o perfil é autorizado
        perfil = st.session_state.get("usuario_perfil")
        if perfil == "Boleiro":
            st.error("🚫 Acesso negado: Apenas Quadras e Clubes podem realizar postagens.")
            st.stop()
        
        # 2. Verifica Pagamento (A barreira)
        conn = criar_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT data_expiracao FROM usuarios WHERE id_usuario = %s", (st.session_state["usuario_id"],))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        data_exp = user_data.get('data_expiracao') if user_data else None
        hoje = dt_modulo.date.today()
        
        # --- BLOCO ÚNICO DE VERIFICAÇÃO ---
        if data_exp is None or data_exp < hoje:
            st.warning("⚠️ Seu acesso precisa ser renovado.")
            
            # 1. Verifica se já existe solicitação PENDENTE
            conn = criar_conexao()
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM solicitacoes_pagamento WHERE id_usuario = %s ORDER BY id DESC LIMIT 1", (st.session_state["usuario_id"],))
            resultado = cursor.fetchone()
            conn.close()

            # 2. Se já existe, apenas avisa e PARA o código aqui
            if resultado and resultado[0] == 'Pendente':
                st.info("🕒 Comprovante já enviado! Nossa equipe levará até 3 dias úteis para aprovar.")
                st.stop() # Interrompe a execução do restante da função (não mostra o resto da aba)

            # 3. Se NÃO existe solicitação, mostra o formulário de pagamento UMA VEZ
            with st.container(border=True):
                st.subheader("💳 Pagamento da Mensalidade")
                st.write("Para liberar seu acesso, realize o Pix:")
                st.code("11957314293", language="text")
                st.caption("nome da entidade: Lucas Da Silva Beserra")
                
                comprovante = st.file_uploader(
                    "Envie o print do seu comprovante Pix:", 
                    type=['jpg', 'png', 'jpeg'], 
                    key="uploader_pagamento_mensalidade"
                )
                
                if comprovante and st.button("Enviar para aprovação"):
                    pasta_fotos = "uploads_comprovantes"
                    if not os.path.exists(pasta_fotos):
                        os.makedirs(pasta_fotos)

                    caminho_completo = os.path.join(pasta_fotos, f"user_{st.session_state['usuario_id']}_{comprovante.name}")
                    
                    with open(caminho_completo, "wb") as f:
                        f.write(comprovante.getbuffer())
                    
                    conn = criar_conexao() # 1. Garantir que a conexão seja criada
                    conn = criar_conexao() # 1. Garantir que a conexão seja criada

                    if conn is not None: # 2. Verificar se a conexão realmente funcionou
                        try:
                            cursor = conn.cursor() # 3. Agora sim, criar o cursor
                            cursor.execute("""
                                INSERT INTO solicitacoes_pagamento 
                                (id_usuario, nome_usuario, caminho_comprovante, status) 
                                VALUES (%s, %s, %s, 'Pendente')
                            """, (st.session_state["usuario_id"], st.session_state["usuario_nome"], caminho_completo))
                            
                            conn.commit()
                            cursor.close()
                            conn.close()
                            
                            st.success("Comprovante enviado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar no banco: {e}")
                            if 'conn' in locals() and conn:
                                conn.close()
                    else:
                        st.error("Erro crítico: Não foi possível conectar ao banco de dados.")
            st.stop()
            
            
            
        
            
            # 1. VERIFICA SE JÁ EXISTE UMA SOLICITAÇÃO PENDENTE
            conn = criar_conexao()
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM solicitacoes_pagamento WHERE id_usuario = %s ORDER BY id DESC LIMIT 1", (st.session_state["usuario_id"],))
            resultado = cursor.fetchone()
            conn.close()

            # 2. SE JÁ EXISTE SOLICITAÇÃO PENDENTE, APENAS AVISA E PARA
            if resultado and resultado[0] == 'Pendente':
                st.info("🕒 Comprovante recebido! Nossa equipe levará até 3 dias úteis para aprovar seu acesso.")
                st.stop() # O código para aqui, o formulário de upload NÃO aparece

                cursor.execute("INSERT INTO solicitacoes_pagamento (id_usuario, nome_usuario, caminho_comprovante, status) VALUES (%s, %s, %s, 'Pendente')", 
                            (st.session_state["usuario_id"], st.session_state["usuario_nome"], caminho_completo))
                conn.commit()
                registrar_notificacao(st.session_state["usuario_id"], "Comprovante enviado! A análise pode levar até 3 dias úteis.")
                conn.close()
                
                st.success("Comprovante enviado! Aguarde a aprovação do Admin.")
                st.rerun() # Recarrega a página, e agora a verificação do passo 1 vai mostrar o aviso

            
        st.markdown("### 📝 Nova Postagem")
        with st.form("form_post_quadra", clear_on_submit=True):
            endereco_arena = st.text_input("Endereço da Arena")
            nome_arena = st.text_input("Nome da Arena")
            tipo_post = st.selectbox("Tipo de Anúncio", ["Geral", "🔥 Promoção Relâmpago", "⏳ Horário Vago", "Eventos / Torneios"])
            conteudo = st.text_area("Descrição da oferta:") # Adicionei este campo que faltava
            col1, col2, col3 = st.columns(3)
            with col1: data_jogo = st.date_input("Data")
            with col2: hora_jogo = st.time_input("Hora")
            with col3: valor_quadra = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            
            botao_postar = st.form_submit_button("🚀 Publicar no Mural")
            
            if botao_postar:
                conn = criar_conexao()
                cursor = conn.cursor()
                
                # PASSO 1: Salva na peladas_ativas
                sql_pelada = """INSERT INTO peladas_ativas 
                (nome_alfa, id_alfa, nome_jogo, nome_arena, data_hora, valor_pix) 
                VALUES (%s, %s, %s, %s, %s, %s)"""
                
                cursor.execute(sql_pelada, (
                    'Aguardando Organizador', 0, f"Pelada em {nome_arena}", nome_arena, f"{data_jogo} {hora_jogo}", valor_quadra
                ))
                id_gerado = cursor.lastrowid
                
                # PASSO 2: Salva na postagens_quadras (Para aparecer no Mural)
                sql_post = """INSERT INTO postagens_quadras 
                (nome_arena, endereco_arena, conteudo, tag_promocao, data_jogo, hora_jogo, valor, id_pelada_vinculada) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                
                cursor.execute(sql_post, (
                    nome_arena, endereco_arena, conteudo, tipo_post, data_jogo, hora_jogo, valor_quadra, id_gerado
                ))
                
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Postagem realizada com sucesso!")
                st.rerun() # Isso força o Mural a recarregar e mostrar o novo post

def exibir_aba_clubes():
    st.subheader("🛡️ Central dos Clubes & Equipes")
    st.markdown("Fique por dentro de peneiras, amistosos e novidades dos times da região.")
    
    sub_aba1, sub_aba2 = st.tabs(["📢 Mural de Avisos", "✍️ Nova Postagem do Clube"])
    
    # ==========================================
    # SUB-ABA 1: O FEED RECENTE DOS CLUBES
    # ==========================================
    with sub_aba1:
        st.markdown("### 📰 Publicações Recentes")
        
        conn = None
        try:
            conn = criar_conexao()
            # 🔄 Buscando as novas colunas de contato do banco
            query = """
            SELECT nome_clube, conteudo, tag_aviso, zap_contato, email_contato, 
            nome_arquivo_media,TO_CHAR(data_postagem, 'YYYY-MM-DD') as data 
            FROM postagens_clubes 
            ORDER BY data_postagem DESC
            """
            df_posts = pd.read_sql(query, conn)
            
            if not df_posts.empty:
                for idx, post in df_posts.iterrows():
                    with st.container(border=True):
                        st.markdown(f"#### **{post['nome_clube']}**")
                        st.caption(f"📌 Tipo: `{post['tag_aviso']}`")
                        
                        st.markdown(post['conteudo'])
                        st.write("") 

                        if post['nome_arquivo_media']:
                            caminho = os.path.join("media", post['nome_arquivo_media'])
                            if os.path.exists(caminho):
                                if post['nome_arquivo_media'].lower().endswith(('.mp4', '.mov')):
                                    st.video(caminho)
                                else:
                                    st.image(caminho, use_container_width=True)
                        
                        # Identifica o melhor texto para a ação baseado no tipo de post
                        texto_whatsapp = "📱 Chamar no WhatsApp"
                        texto_email = "✉️ Enviar E-mail"
                        if "amistoso" in post['conteudo'].lower() or "desafio" in post['conteudo'].lower():
                            texto_whatsapp = "⚔️ Aceitar Desafio (WhatsApp)"
                            texto_email = "⚔️ Aceitar Desafio (E-mail)"
                        elif "peneira" in post['conteudo'].lower() or "vaga" in post['conteudo'].lower():
                            texto_whatsapp = "📋 Candidatar-se via WhatsApp"
                            texto_email = "📋 Enviar Currículo por E-mail"
                        
                        # 🔄 LÓGICA DE EXIBIÇÃO DOS BOTÕES COM FOCO MOBILE
                        tem_zap = post['zap_contato'] and str(post['zap_contato']).strip() != ""
                        tem_email = post['email_contato'] and str(post['email_contato']).strip() != ""
                        
                        # Se tiver WhatsApp, renderiza o botão de link direto
                        if tem_zap:
                            # Remove caracteres do número caso o usuário digite com traço ou parênteses
                            num_limpo = "".join(filter(str.isdigit, str(post['zap_contato'])))
                            # Texto pré-definido para facilitar a vida do usuário no celular
                            mensagem_pronta = f"Olá! Vi a sua publicação do {post['nome_clube']} no app NextDraft e fiquei interessado."
                            link_zap = f"https://wa.me/{num_limpo}?text={mensagem_pronta.replace(' ', '%20')}"
                            
                            st.link_button(texto_whatsapp, link_zap, use_container_width=True)
                        
                        # Se tiver E-mail, renderiza o botão de e-mail (mailto)
                        if tem_email:
                            email_limpo = str(post['email_contato']).strip()
                            assunto_pronto = f"Contato via NextDraft - {post['nome_clube']}"
                            link_email = f"mailto:{email_limpo}?subject={assunto_pronto.replace(' ', '%20')}"
                            
                            st.link_button(texto_email, link_email, use_container_width=True)
                        
                        # --- RODAPÉ DE CONTATO SECUNDÁRIO (Texto de segurança) ---
                        if tem_email or tem_zap:
                            contatos_texto = []
                            if tem_zap: contatos_texto.append(f"WhatsApp: {post['zap_contato']}")
                            if tem_email: contatos_texto.append(f"E-mail: {post['email_contato']}")
                            st.caption(f"📞 Contato direto: {' | '.join(contatos_texto)}")
                            
                        st.caption(f"🕒 Publicado em: {post['data']}")
                            
            else:
                st.info("Nenhum clube postou no mural ainda. Seja o primeiro!")
                
        except Exception as e:
            st.error(f"Erro ao carregar o mural dos clubes: {e}")
        finally:
            if conn:
                conn.close()

    # ==========================================
    # SUB-ABA 2: FORMULÁRIO DE POSTAGEM
    # ==========================================
    with sub_aba2:

        # 1. Verifica se o perfil é autorizado
        perfil = st.session_state.get("usuario_perfil")
        if perfil == "Boleiro":
            st.error("🚫 Acesso negado: Apenas Quadras e Clubes podem realizar postagens.")
            st.stop()

        st.markdown("### 📝 Criar Comunicado Oficial")        
        
        with st.form("form_post_clube", clear_on_submit=True):
            nome_clube = st.text_input("Nome do seu Clube/Time")
            tipo_aviso = st.selectbox("Tipo de Publicação", ["Geral", "Peneira / Teste", "Procura-se Amistoso", "Contratação"])
            conteudo_post = st.text_area("O que você quer comunicar aos boleiros?")
            
            st.markdown("---")
            st.markdown("##### 📞 Canais de Contato (Preencha pelo menos um)")
            whatsapp_input = st.text_input("WhatsApp para contato (com DDD):")
            email_input = st.text_input("E-mail para contato:")
            arquivo_midia = st.file_uploader("Foto ou Vídeo do seu Clube", type=['jpg', 'jpeg', 'png', 'mp4'])
            
            botao_postar = st.form_submit_button("🚀 Publicar no Mural", use_container_width=True)
    
    # AGORA, A LÓGICA ESTÁ DENTRO DO IF DO BOTÃO
        if botao_postar:
            if not nome_clube.strip() or not conteudo_post.strip():
                st.warning("Por favor, preencha o nome do clube e o conteúdo do post!")
            elif not whatsapp_input.strip() and not email_input.strip():
                st.warning("Por favor, forneça pelo menos uma forma de contato!")
            else:
                # Garante a pasta
                if not os.path.exists("media"):
                    os.makedirs("media")
                
                nome_arquivo = None
                if arquivo_midia:
                    nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo_midia.name}"
                    with open(os.path.join("media", nome_arquivo), "wb") as f:
                        f.write(arquivo_midia.getbuffer())
            
            conn = None
            cursor = None
            try:
                conn = criar_conexao()
                cursor = conn.cursor()
                sql = """INSERT INTO postagens_clubes 
                         (nome_clube, conteudo, tag_aviso, zap_contato, email_contato, data_postagem, nome_arquivo_media) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (nome_clube.strip(), conteudo_post.strip(), tipo_aviso, whatsapp_input.strip(), email_input.strip(), datetime.now(), nome_arquivo))
                conn.commit()
                
                st.success("Postagem publicada com sucesso!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar postagem: {e}")
            finally:
                if cursor: cursor.close()
                if conn and conn.is_connected(): conn.close()

def exibir_aba_boleiros():
        
    st.title("🏃 Central dos Boleiros")
    st.markdown("Monte seu racha, escale os times visualmente e gerencie as finanças do jogo.")

    # Resgatando os dados reais do atleta logado na sessão ativa
    id_usuario_atual = int(st.session_state['usuario_id'])
    nome_usuario_atual = st.session_state.get('usuario_nome', 'Jogador')
    overall_usuario_atual = int(st.session_state.get('usuario_overall', 60))

    menu_boleiro = st.tabs(["⚽ Peladas em Aberto", "➕ Criar Nova Pelada", "🛡️ Painel do Organizador (Alfa)"])

    # ==========================================================
    # SUB-ABA 1: VISUALIZAR PELADAS E CAMPINHO (BLINDADA CONTRA ERROS)
    # ==========================================================
    with menu_boleiro[0]:
        st.subheader("Peladas com Vagas Disponíveis")
        
        conn = None
        try:
            conn = criar_conexao()
            
            # No seu código atual, procure o comando de SELECT e troque por este:
            query = """
    SELECT * FROM peladas_ativas 
    WHERE (status_jogo IS NULL OR status_jogo = 'Aberto')
"""
            df_jogos = pd.read_sql(query, conn)
            
            if df_jogos.empty:
                st.info("Nenhuma pelada precisando de jogadores no momento. Crie uma!")
            else:
                for _, jogo in df_jogos.iterrows():
                    with st.container(border=True):
                        st.markdown(f"### **{jogo['nome_jogo']}**")
                        st.markdown(f"🏟️ **Local:** {jogo['nome_arena']} | 📍 {jogo['endereco_arena']}")
                        st.markdown(f"📅 **Data/Hora:** {jogo['data_hora']} | 💵 **Valor da quadra:** R$ {jogo['valor_pix']:.2f}")
                        st.markdown(f"👤 **Organizador (Alfa):** {jogo['nome_alfa']}")
                        
                        # Buscar jogadores já confirmados neste jogo
                        query_esc = "SELECT * FROM escalacao_pelada WHERE id_pelada = %s AND status_vaga = 'Confirmado'"
                        df_esc = pd.read_sql(query_esc, conn, params=[jogo['id_pelada']])
                        
                        # --- RENDERIZAÇÃO DO CAMPINHO VISUAL SIMPLIFICADO ---
                        st.markdown("#### 🏟️ **Escalação em Tempo Real**")
                        
                        # CORREÇÃO RESPONSIVA: Trocando colunas por abas para não vazar no celular
                        abas_times = st.tabs(["🟢 Colete Verde", "⚫ Colete Preto"])
                        
                        with abas_times[0]:
                            # 🔥 TRAVA DE SEGURANÇA: Se a tabela de escalação estiver vazia para este jogo, evita o erro do Pandas
                            if not df_esc.empty and 'time_escalado' in df_esc.columns:
                                goleiro_a = df_esc[(df_esc['time_escalado'] == 'verde') & (df_esc['posicao_quadra'] == 'Goleiro')]
                                linhas_a = df_esc[(df_esc['time_escalado'] == 'verde') & (df_esc['posicao_quadra'] == 'Linha')]
                            else:
                                goleiro_a = pd.DataFrame()
                                linhas_a = pd.DataFrame()
                            
                            st.markdown(f"🧤 **Goleiro:** {goleiro_a['nome_jogador'].values[0] if not goleiro_a.empty else '❌ Vago'}")
                            st.markdown("**Linhas:**")
                            for i in range(int(jogo['max_linha_por_time'])):
                                if i < len(linhas_a):
                                    player = linhas_a.iloc[i]
                                    st.markdown(f"🏃 {player['nome_jogador']} *(Ovr: {player['overall_jogador']})*")
                                else:
                                    st.markdown("⬜ *Vaga Disponível*")
                                    
                        with abas_times[1]:
                            # 🔥 TRAVA DE SEGURANÇA SEGUNDO TIME
                            if not df_esc.empty and 'time_escalado' in df_esc.columns:
                                goleiro_b = df_esc[(df_esc['time_escalado'] == 'preto') & (df_esc['posicao_quadra'] == 'Goleiro')]
                                linhas_b = df_esc[(df_esc['time_escalado'] == 'preto') & (df_esc['posicao_quadra'] == 'Linha')]
                            else:
                                goleiro_b = pd.DataFrame()
                                linhas_b = pd.DataFrame()
                            
                            st.markdown(f"🧤 **Goleiro:** {goleiro_b['nome_jogador'].values[0] if not goleiro_b.empty else '❌ Vago'}")
                            st.markdown("**Linhas:**")
                            for i in range(int(jogo['max_linha_por_time'])):
                                if i < len(linhas_b):
                                    player = linhas_b.iloc[i]
                                    st.markdown(f"🏃 {player['nome_jogador']} *(Ovr: {player['overall_jogador']})*")
                                else:
                                    st.markdown("⬜ *Vaga Disponível*")
                        
                        # Lista de Reservas com checagem de segurança
                        if not df_esc.empty and 'time_escalado' in df_esc.columns:
                            reservas = df_esc[df_esc['time_escalado'] == 'RESERVA']
                        else:
                            reservas = pd.DataFrame()
                            
                        if not reservas.empty:
                            st.markdown("**📋 Lista de Reservas:**")
                            for _, res in reservas.iterrows():
                                st.caption(f"⏳ {res['nome_jogador']} ({res['posicao_quadra'] if 'posicao_quadra' in res else 'Linha'})")
                        
                        st.markdown("---")
                        
                        with st.expander("➕ Pedir para Entrar nesta Pelada"):
                            time_desejado = st.selectbox("Escolha o Colete", ["verde", "preto", "RESERVA"], key=f"time_{jogo['id_pelada']}")
                            pos_desejada = st.selectbox("Posição", ["Linha", "Goleiro"], key=f"pos_{jogo['id_pelada']}")
                            
                            if st.button("Mandar Cartinha para o Alfa", key=f"btn_entrar_{jogo['id_pelada']}", use_container_width=True):
                                try:
                                    cursor = conn.cursor()
                                    
                                    # 1. Insere a solicitação na escalação
                                    sql_ins = """INSERT INTO escalacao_pelada (id_pelada, id_jogador, nome_jogador, overall_jogador, time_escalado, posicao_quadra, status_vaga) 
                                                VALUES (%s, %s, %s, %s, %s, %s, 'Pendente')"""
                                    cursor.execute(sql_ins, (jogo['id_pelada'], id_usuario_atual, nome_usuario_atual, overall_usuario_atual, time_desejado, pos_desejada))
                                    
                                    # 2. Insere a mensagem automática no CHAT para o Alfa ver
                                    msg_notificacao = f"📩 O boleiro {nome_usuario_atual} solicitou uma vaga para esta pelada! (Status: Pendente)"
                                    sql_chat = """INSERT INTO mensagens_chat (id_envia, nome_envia, id_pelada, id_recebe, mensagem) 
                                                VALUES (%s, %s, %s,0, %s)"""
                                    # id_envia = 0 (Sistema/Notificação)
                                    cursor.execute(sql_chat, (0, "Sistema", jogo['id_pelada'], msg_notificacao))
                                    registrar_notificacao(jogo['id_alfa'], msg_notificacao)

                                    conn.commit()
                                    st.success("Sua solicitação foi enviada para o Boleiro Alfa! Aguarde a aprovação.")                
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Erro ao solicitar vaga: {err}")
        except Exception as e:
            st.error(f"Erro ao carregar peladas: {e}")
        finally:
            if conn:
                conn.close()

    # ==========================================================
    # SUB-ABA 2: CRIAR UM NOVO JOGO / REPOSTAR HORÁRIO
    # ==========================================================
    with menu_boleiro[1]:
        st.subheader("Organizar uma nova Pelada")
        with st.form("form_criar_pelada", clear_on_submit=True):
            nome_jogo = st.text_input("Nome do Racha", placeholder="Ex: Clássico das Terças")
            nome_arena = st.text_input("Nome da Quadra/Arena", placeholder="Ex: Arena Soccer Pro")
            endereco_arena = st.text_input("Endereço Completo", placeholder="Av. Principal, 450 - Centro")
            data_hora = st.date_input("Dia do Jogo")
            max_jogadores = st.number_input("Jogadores de linha por time (Ex: 5 para Society padrão)", min_value=3, max_value=11, value=5)
            valor_pix = st.number_input("Valor da vaquinha por jogador (R$)", min_value=0.0, value=15.00)
            chave_pix = st.text_input("Chave PIX do Organizador Alfa (para receber a taxa)", placeholder="Ex: celular, e-mail ou aleatória")
            
            botao_criar = st.form_submit_button("🚀 Criar Pelada e Abrir Campinho")
            
            if botao_criar:
                if not nome_jogo or not nome_arena:
                    st.warning("Preencha o nome do racha e da arena!")
                else:
                    conn = None
                    try:
                        conn = criar_conexao()
                        cursor = conn.cursor()
                        sql = """INSERT INTO peladas_ativas (nome_jogo, nome_arena, endereco_arena, data_hora, id_alfa, nome_alfa, max_linha_por_time, valor_pix, chave_pix) 
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        cursor.execute(sql, (nome_jogo, nome_arena, endereco_arena, data_hora, id_usuario_atual, nome_usuario_atual, max_jogadores, valor_pix, chave_pix))
                        conn.commit()
                        st.success("Pelada criada com sucesso! Corra para a aba 'Peladas em Aberto' para gerenciar.")
                        cursor.close()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar jogo: {e}")
                    finally:
                        if conn and conn.is_connected():
                            conn.close()

    # ==========================================================
    # SUB-ABA 3: PAINEL DO ALFA (APROVAÇÕES)
    # ==========================================================
    with menu_boleiro[2]:
        st.subheader("📥 Solicitações de Atletas para Seus Jogos")
        conn = None
        try:
            conn = criar_conexao()
       
           
            query_pedidos = """
                    SELECT e.*, p.nome_jogo 
                    FROM escalacao_pelada e
                    INNER JOIN peladas_ativas p ON e.id_pelada = p.id_pelada
                    WHERE p.id_alfa = %s AND e.status_vaga = 'Pendente'
                """
            df_pedidos = pd.read_sql(query_pedidos, conn, params=[id_usuario_atual])
            
            if df_pedidos.empty:
                st.info("Nenhuma solicitação pendente para as suas peladas no momento.")
            else:
                for _, pedido in df_pedidos.iterrows():
                    # ... (seu código atual de exibir solicitações fica exatamente igual aqui) ...
                    with st.container(border=True):
                        st.write(f"🏃 **{pedido['nome_jogador']}** quer entrar no jogo **{pedido['nome_jogo']}**")
                        st.caption(f"Posição pedida: `{pedido['posicao_quadra']}` | Colete pretendido: Colete `{pedido['time_escalado']}`")
                        
                        # Botão Aceitar
                    if st.button("✅ Aceitar no Jogo", key=f"rec_acc_{pedido['id_escalacao']}"):
                        conn_tmp = criar_conexao() # Abre conexão nova
                        cursor = conn_tmp.cursor()
                        registrar_notificacao(pedido['id_jogador'], f"✅ Parabéns! O Boleiro Alfa aceitou sua vaga no racha.")
                        cursor.execute("UPDATE escalacao_pelada SET status_vaga = 'Confirmado' WHERE id_escalacao = %s", [pedido['id_escalacao']])
                        conn_tmp.commit()
                        cursor.close()
                        conn_tmp.close() # Fecha conexão
                        st.success("Adicionado!")
                        st.rerun()

                    # Botão Recusar
                    if st.button("❌ Recusar Solicitação", key=f"rec_dec_{pedido['id_escalacao']}", use_container_width=True):
                        conn_tmp = criar_conexao() # Abre conexão nova
                        cursor = conn_tmp.cursor()
                        registrar_notificacao(pedido['id_jogador'], f"❌ Infelizmente sua solicitação para o racha foi recusada.")
                        cursor.execute("DELETE FROM escalacao_pelada WHERE id_escalacao = %s", [pedido['id_escalacao']])
                        conn_tmp.commit()
                        cursor.close()
                        conn_tmp.close() # Fecha conexão (ESSENCIAL)
                        st.success("Solicitação recusada.")
                        st.rerun()
            # --- NOVO BLOCO: ADIÇÃO MANUAL ---
            st.markdown("---")
            with st.expander("➕ Adicionar boleiro manualmente"):
                # Primeiro, seleciona qual jogo (apenas os jogos que esse usuário é Alfa)
                query_meus_jogos = "SELECT id_pelada, nome_jogo FROM peladas_ativas WHERE id_alfa = %s"
                df_meus_jogos = pd.read_sql(query_meus_jogos, conn, params=[id_usuario_atual])
                
                if not df_meus_jogos.empty:
                    jogo_escolhido = st.selectbox("Escolha o jogo:", df_meus_jogos['nome_jogo'])
                    id_pelada_escolhida = df_meus_jogos.loc[df_meus_jogos['nome_jogo'] == jogo_escolhido, 'id_pelada'].values[0]
                    
                    nome_manual = st.text_input("Nome do Boleiro:")
                    if st.button("Adicionar ao Jogo"):
                        cursor = conn.cursor()
                        cursor.execute("""
                        INSERT INTO escalacao_pelada (id_pelada, id_jogador, nome_jogador, overall_jogador, time_escalado, posicao_quadra, status_vaga) 
                        VALUES (%s, 0, %s, 60, %s, %s, 'Confirmado')
                    """, (int(id_pelada_escolhida), nome_manual, 'A', 'Linha'))
                        conn.commit()
                        cursor.close()
                        st.success(f"{nome_manual} adicionado com sucesso! Ele já pode ver o chat.")
                        st.rerun()
            # ---------------------------------
                
        except Exception as e:
            st.error(f"Erro no painel do organizador: {e}")
        finally:
            if conn:
                conn.close()

def exibir_perfil():
    # Pegando os dados reais do usuário logado na sessão do banco
    id_usuario_atual = int(st.session_state["usuario_id"])
    nome_usuario_atual = st.session_state.get("username", "Visitante")
    perfil_usuario_atual = st.session_state["usuario_perfil"]
    
    # 1. CARREGAMENTO PRÉVIO DOS DADOS (Evita quebra de escopo das variáveis)
    habilidades = None
    foto_banco = None
    conn = None
    
    try:
        conn = criar_conexao()
        cursor = conn.cursor()
        
        # Buscamos as notas do atleta
        cursor.execute("SELECT nota_velocidade, nota_passe, nota_fisico, nota_finalizacao, nota_drible, nota_defesa FROM habilidades_atletas WHERE id_atleta = %s", (id_usuario_atual,))
        res_hab = cursor.fetchone()
        if res_hab:
            habilidades = {
                'nota_velocidade': res_hab[0], 'nota_passe': res_hab[1], 'nota_fisico': res_hab[2],
                'nota_finalizacao': res_hab[3], 'nota_drible': res_hab[4], 'nota_defesa': res_hab[5]
            }
        
        # Buscamos a foto do atleta na tabela de usuários (usando índice 0 para evitar o erro de dicionário)
        cursor.execute("SELECT foto_perfil FROM usuarios WHERE id_usuario = %s", (id_usuario_atual,))
        dados_foto = cursor.fetchone()
        if dados_foto and dados_foto[0]:
            foto_banco = dados_foto[0]
            
        cursor.close()
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        if conn:
            conn.close()

    # Se não existir histórico no banco, define valores padrão (60)
    if not habilidades:
        habilidades = {
            'nota_velocidade': 60, 'nota_passe': 60, 'nota_fisico': 60,
            'nota_finalizacao': 60, 'nota_drible': 60, 'nota_defesa': 60
        }

    # Pré-calcula os atributos para o Card usar antes dos Sliders (evita bug de reatividade)
    vel_atual = int(habilidades['nota_velocidade'])
    pas_atual = int(habilidades['nota_passe'])
    fin_atual = int(habilidades['nota_finalizacao'])
    dri_atual = int(habilidades['nota_drible'])
    def_atual = int(habilidades['nota_defesa'])
    fis_atual = int(habilidades['nota_fisico'])

    # --- 1. O CARD TÁTICO AGORA NO TOPO DA TELA ---
    overall = int((vel_atual + pas_atual + fis_atual + fin_atual + dri_atual + def_atual) / 6)
    
    if overall >= 80:
        cor_borda = "linear-gradient(135deg, #ffe066, #f5b041)"
        cor_texto_tipo = "#f5b041"
    elif overall >= 70:
        cor_borda = "linear-gradient(135deg, #d5dbdb, #95a5a6)"
        cor_texto_tipo = "#95a5a6"
    else:
        cor_borda = "linear-gradient(135deg, #edbb99, #a04000)"
        cor_texto_tipo = "#a04000"

    foto_avatar_src = foto_banco if foto_banco else "https://www.w3schools.com/howto/img_avatar.png"

    html_card = f"""
    <div style="background: #111; background-image: radial-gradient(circle at 50% 20%, #222 0%, #111 80%); border: 4px solid; border-image: {cor_borda} 1; border-radius: 15px; padding: 25px; max-width: 100%; width: 280px; font-family: 'Arial', sans-serif; color: white; box-shadow: 0px 10px 20px rgba(0,0,0,0.5); margin: 20px auto; display: flex; flex-direction: column;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 10px;">
            <div>
                <div style="font-size: 42px; font-weight: bold; line-height: 38px; color: white;">{overall}</div>
                <div style="font-size: 14px; font-weight: bold; color: {cor_texto_tipo}; letter-spacing: 1px;">ATLETA</div>
            </div>
            <img src="{foto_avatar_src}" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover; border: 2px solid #fff; background-color: #222;">
        </div>
        <div style="text-align: center; margin: 20px 0;">
            <div style="font-size: 22px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">{nome_usuario_atual.split()[0] if nome_usuario_atual else "JOGADOR"}</div>
            <div style="font-size: 11px; color: #888; margin-top: 3px;">📍 Verificado via App</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px 20px; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; border: 1px solid #222;">
            <div style="display: flex; justify-content: space-between;"><span style="color:#aaa; font-size:13px;">VEL</span> <strong style="font-size:14px;">{vel_atual}</strong></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#aaa; font-size:13px;">FIN</span> <strong style="font-size:14px;">{fin_atual}</strong></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#aaa; font-size:13px;">PAS</span> <strong style="font-size:14px;">{pas_atual}</strong></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#aaa; font-size:13px;">DRI</span> <strong style="font-size:14px;">{dri_atual}</strong></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#aaa; font-size:13px;">DEF</span> <strong style="font-size:14px;">{def_atual}</strong></div>
            <div style="display: flex; justify-content: space-between;"><span style="color:#aaa; font-size:13px;">FIS</span> <strong style="font-size:14px;">{fis_atual}</strong></div>
        </div>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. SEÇÃO DE INFORMAÇÕES DO USUÁRIO ---
    st.subheader("📋 Suas Informações")
    with st.container(border=True):
        st.markdown(f"**Nome:** {nome_usuario_atual}")
        st.markdown(f"**Tipo de Perfil:** `{perfil_usuario_atual}`")

    # --- 3. SEÇÃO DE UPLOAD DE FOTO ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("📷 **Sua Foto do Card**")
    arquivo_foto = st.file_uploader("Escolha uma foto para o seu Card", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    if arquivo_foto is not None:
        bytes_data = arquivo_foto.read()
        base64_foto = base64.b64encode(bytes_data).decode()
        foto_avatar_src = f"data:image/png;base64,{base64_foto}"
        
        try:
            conn = criar_conexao()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET foto_perfil = %s WHERE id_usuario = %s", (foto_avatar_src, id_usuario_atual))
            conn.commit()
            cursor.close()
            conn.close()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar a foto: {e}")

    # --- 4. ATUALIZAR ATRIBUTOS ---
    st.markdown("---")
    st.subheader("⚡ Atualizar Atributos (Modo Atleta)")
    
    vel = st.slider("Velocidade (VEL)", 10, 99, vel_atual)
    pas = st.slider("Passe (PAS)", 10, 99, pas_atual)
    fin = st.slider("Finalização (FIN)", 10, 99, fin_atual)
    dri = st.slider("Dribles (DRI)", 10, 99, dri_atual)
    def_nota = st.slider("Defesa (DEF)", 10, 99, def_atual)
    fis = st.slider("Físico (FIS)", 10, 99, fis_atual)
    
    if st.button("💾 Salvar Atributos no Banco", use_container_width=True):
        try:
            conn = criar_conexao()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_atleta FROM habilidades_atletas WHERE id_atleta = %s", (id_usuario_atual,))
            existe = cursor.fetchone()
            
            if existe:
                sql = """UPDATE habilidades_atletas SET nota_velocidade=%s, nota_passe=%s, nota_fisico=%s, 
                         nota_finalizacao=%s, nota_drible=%s, nota_defesa=%s WHERE id_atleta=%s"""
                cursor.execute(sql, (vel, pas, fis, fin, dri, def_nota, id_usuario_atual))
            else:
                # Ajustado para incluir o campo username e evitar o erro de NOT-NULL constraint
                cursor.execute("INSERT INTO atletas (id_atleta, username, nome, email, senha, posicao_principal, cidade, estado) VALUES (%s, %s, %s, %s, '123456', 'Meia', 'São Paulo', 'SP')", (id_usuario_atual, nome_usuario_atual, nome_usuario_atual, f"{nome_usuario_atual.lower()}@email.com"))
                sql = """INSERT INTO habilidades_atletas (id_atleta, nota_velocidade, nota_passe, nota_fisico, 
                         nota_finalizacao, nota_drible, nota_defesa) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (id_usuario_atual, vel, pas, fis, fin, dri, def_nota))
            
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Habilidades salvas! O seu card tático foi recalculado.")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar atributos: {e}")

@st.dialog("📖 Story do Parceiro")
def abrir_story_parceiro(nome_parceiro):
    conn = None
    try:
        conn = criar_conexao()
        # Busca a última postagem ativa desse parceiro específico
        query = "SELECT imagem_story, texto_story, link_cupom FROM stories_parceiros WHERE nome_parceiro = %s ORDER BY data_postagem DESC LIMIT 1"
        df_story = pd.read_sql(query, conn, params=[nome_parceiro])
        
        if not df_story.empty:
            story = df_story.iloc[0]
            
            st.markdown(f"### ⚡ **{nome_parceiro}**")
            
            # Mostra a imagem do produto/postagem se houver
            if story['imagem_story']:
                st.image(story['imagem_story'], use_container_width=True)
                
            # Texto do anúncio
            st.markdown(f" {story['texto_story']}")
            
            # Cupom ou Ação especial
            if story['link_cupom']:
                st.success(f"🎟️ Cupom de Desconto: `{story['link_cupom']}`")
                
            if st.button("🚀 Aproveitar Oferta", use_container_width=True):
                st.toast("Redirecionando para o parceiro...")
        else:
            # Caso o parceiro ainda não tenha postado nada no banco
            st.markdown(f"### 🏟️ **{nome_parceiro}**")
            st.info("Este parceiro ainda não publicou ofertas hoje. Fique ligado para os próximos rachas!")
            
    except Exception as e:
        st.error(f"Erro ao carregar Story: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

def exibir_aba_notificacoes():
    st.markdown("### 🔔 Suas Notificações")
    st.caption("Fique por dentro de quem te mandou mensagem, curtiu ou comentou nas suas publicações.")
    
    id_usuario_atual = st.session_state.get("usuario_id")
    
    conn = None
    try:
        conn = criar_conexao()
        
        # 1. BUSCA AS NOTIFICAÇÕES REAIS DO USUÁRIO LOGADO
        query = """
            SELECT id_notificacao, mensagem, lida, data_envio 
            FROM notificacoes 
            WHERE id_usuario_destino = %s 
            ORDER BY data_envio DESC 
            LIMIT 30
        """
        df_notifs = pd.read_sql(query, conn, params=[id_usuario_atual])
        
        # 2. SE HOUVER NOTIFICAÇÕES, EXIBE NA TELA DO CELULAR
        if not df_notifs.empty:
            for _, notif in df_notifs.iterrows():
                # Se lida for False (0), coloca a bolinha azul do Instagram de "Nova"
                status_lida = "🔵 " if not notif['lida'] else "   "
                
                # Renderiza a linha com espaçamento limpo para o polegar
                st.markdown(
                    f"<div style='padding: 10px 0; border-bottom: 1px solid #222;'>"
                    f"{status_lida} {notif['mensagem']} "
                    f"<br><small style='color: #8e8e8e; margin-left: 25px;'>{notif['data_envio'].strftime('%d/%m às %H:%M')}</small>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
            
            # 3. MARCA TODAS AS NOTIFICAÇÕES DESSE USUÁRIO COMO LIDAS AUTOMATICAMENTE
            cursor = conn.cursor()
            cursor.execute("UPDATE notificacoes SET lida = TRUE WHERE id_usuario_destino = %s", (id_usuario_atual,))
            conn.commit()
            cursor.close()
            
        else:
            st.info("Você está atualizado! Nenhuma nova notificação por aqui.")
            
    except Exception as e:
        st.error(f"Erro ao carregar suas notificações: {e}")
    finally:
        if conn:
            conn.close()

def registrar_notificacao(id_destino, mensagem):
    try:
        conn = criar_conexao()
        cursor = conn.cursor()
        query = "INSERT INTO notificacoes (id_usuario_destino, mensagem, lida, data_envio) VALUES (%s, %s, FALSE, NOW())"
        cursor.execute(query, (id_destino, mensagem))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao registrar notificação: {e}")            

def verificar_acesso_quadra(id_quadra):
    conn = criar_conexao()
    cursor = conn.cursor(dictionary=True)
    
    # AQUI ESTÁ A CORREÇÃO: trocamos 'quadras' por 'peladas'
    # E verifiquei que o campo que você tem é 'id_pelada' (singular)
    cursor.execute("SELECT status_pagamento, data_vencimento_mensalidade FROM peladas WHERE id_pelada = %s", (id_quadra,))
    
    quadra = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not quadra:
        return False
        
    hoje = datetime.now().date()
    
    # Agora a validação vai funcionar porque os nomes das colunas estão corretos
    if quadra['status_pagamento'] != 'pago' or (quadra['data_vencimento_mensalidade'] and quadra['data_vencimento_mensalidade'] < hoje):
        return False
        
    return True

def renderizar_interacoes(post):
    # Aqui você coloca todos os botões que você tem nas outras abas
    if st.button(f"WhatsApp {post['id']}", key=f"wa_{post['id']}"):
        st.write(f"Abrindo WhatsApp para {post['contato']}")
    if st.button(f"E-mail {post['id']}", key=f"em_{post['id']}"):
        st.write("Abrindo e-mail...")

def desenhar_card_postagem(autor, tipo, tag, conteudo, data):
    with st.container(border=True):
        col_autor, col_tag = st.columns([3, 1])
        with col_autor:
            icone = "🛡️" if tipo == 'clube' else "🏟️"
            st.markdown(f"{icone} **{autor}** *({tipo.capitalize()})*")
        with col_tag:
            if tag in ["🔥 Promoção Relâmpago", "⏳ Horário Vago"]:
                st.warning(tag)
            else:
                st.caption(f"📌 `{tag}`")
        st.markdown(conteudo)
        st.caption(f"🕒 Publicado em: {data}")
        # AQUI VOCÊ ADICIONA OS BOTÕES DE INTERAÇÃO QUE VOCÊ QUERIA
        if st.button("💬 Contatar", key=f"btn_{autor}_{hash(conteudo)}"):
            st.info("Funcionalidade de contato em breve!")

def renderizar_post(autor, tipo, tag, conteudo, data):
    with st.container(border=True):
        col_autor, col_tag = st.columns([3, 1])
        with col_autor:
            icone = "🛡️" if tipo == 'clube' else "🏟️"
            st.markdown(f"{icone} **{autor}** *({tipo.capitalize()})*")
        with col_tag:
            if tag in ["🔥 Promoção Relâmpago", "⏳ Horário Vago"]:
                st.warning(tag)
            else:
                st.caption(f"📌 `{tag}`")
        st.markdown(conteudo)
        st.caption(f"🕒 Publicado em: {data}")
# ==========================================



# 4. TELA DE LOGIN E CADASTRO
# ==========================================
if not st.session_state["logado"]:
    st.title("⚽ Rede do Futebol")
    aba_acesso = st.tabs(["🔐 Entrar", "📝 Criar Conta"])

    with aba_acesso[0]: # LOGIN
        email_login = st.text_input("E-mail:", key="login_email")
        senha_login = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar", use_container_width=True):
            conn = criar_conexao()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            # CORRIGIDO: de 'senate_login' para 'senha_login'
            cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email_login, senha_login))
            usuario = cursor.fetchone()

            
            if usuario:
                # Lógica para identificar Admin
                eh_admin = (usuario["email"] == st.secrets["ADMIN_EMAIL"])
                
                
                st.session_state.update({
                    "logado": True, 
                    "usuario_id": usuario["id_usuario"], 
                    "usuario_nome": usuario["username"], 
                    "usuario_perfil": usuario["tipo_perfil"],
                    "is_admin": eh_admin  # <--- Salva no estado do app
                })
                st.rerun()
            else: 
                st.error("E-mail ou senha incorretos.")
            cursor.close()
            conn.close()

    with aba_acesso[1]: # CADASTRO
        tipo_perfil = st.selectbox("Selecione seu Perfil:", ["Boleiro", "Quadra", "Clube"])
        novo_nome = st.text_input("Nome ou Nome do Estabelecimento:", key="cad_nome")
        novo_email = st.text_input("E-mail de Acesso:", key="cad_email")
        nova_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        
       
        
        if st.button("Cadastrar e Entrar", use_container_width=True):
            if len(novo_nome) < 3:
                st.error("O nome precisa ter pelo menos 3 caracteres.")
            elif "@" not in novo_email or "." not in novo_email:
                st.error("E-mail inválido. Por favor, insira um e-mail correto.")
            elif len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                conn = criar_conexao()
                cursor = conn.cursor()
                
                cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (novo_email,))
                if cursor.fetchone():
                    st.error("Este e-mail já está cadastrado em nossa rede!")
                    cursor.close()
                    conn.close()
                else:
                    try:
                        # Inserção preenchendo as colunas obrigatórias mapeadas na tabela da nuvem
                        cursor.execute(
                            """
                            INSERT INTO usuarios (
                                "username", email, senha, tipo_perfil, 
                                legenda_autor, url_avatar, biografia, posição, 
                                tempo_coração, foto_profile, vel, passado, 
                                barbatana, dri, definição, fis, status_conta, status_pagamento
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                            RETURNING id_usuario
                            """, 
                            (
                                novo_nome, novo_email, nova_senha, tipo_perfil,
                                "Membro", "https://www.w3schools.com/howto/img_avatar.png", "Olá!", "Indefinida",
                                "Normal", "https://www.w3schools.com/howto/img_avatar.png", 0, 0,
                                0, 0, 0, 0, "Ativo", "Pendente"
                            )
                        )
                        resultado = cursor.fetchone()
                        conn.commit()
                        
                        if resultado:
                            novo_id = resultado[0]
                            st.session_state.update({
                                "logado": True, 
                                "usuario_id": novo_id, 
                                "usuario_nome": novo_nome, 
                                "usuario_perfil": tipo_perfil
                            })
                            st.rerun()
                        else:
                            st.error("Erro ao recuperar o ID do usuário recém-criado.")
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco: {e}")
                    finally:
                        cursor.close()
                        conn.close()

    st.stop() # Bloqueia o avanço se não estiver logado
# ==========================================



# 5. AMBIENTE LOGADO (Menu na Sidebar)
# ==========================================
nome_usuario_atual = st.session_state.get("usuario_nome", "Visitante")
perfil_usuario_atual = st.session_state.get("usuario_perfil", "Visitante")

opcoes_disponiveis = ["🏠 Home", "🔍 Buscar", "🏃 Boleiros", "💬 Chat", "🔔 Notificações", "👤 Meu Perfil"]
#  ==========================================
perfil_normalizado = str(perfil_usuario_atual).strip().capitalize()


# DEFINE QUEM TEM ACESSO A QUAIS PAGINAS DENTRO DO APP
# ==========================================
if perfil_normalizado in ["Quadra", "Clube"] or st.session_state.get("is_admin", False):
    opcoes_disponiveis.append("🏟️ Quadras")
    opcoes_disponiveis.append("⚽ Clubes")
    
# 3. Se for ADMIN, adiciona o painel extra
if st.session_state.get("is_admin", False) or perfil_normalizado == "Admin":
    opcoes_disponiveis.append("🛠️ Painel Admin")
    opcoes_disponiveis.append("🏢 Gerenciar Espaço")

# Menu renderizado de forma segura dentro da Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {nome_usuario_atual}")
    st.markdown(f"🏷️ Perfil: ` {perfil_usuario_atual} `")
    
    pagina_selecionada = option_menu(
        menu_title="Navegação", 
        options=opcoes_disponiveis,
        key="menu_lateral_futebol_definitivo",
        styles={
            "container": {"background-color": "#1a1a1a"},
            "nav-link": {"color": "#ffffff"},
            "nav-link-selected": {"background-color": "#2e7d32"},
        }
    )
    
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state["logado"] = False
        st.session_state["usuario_id"] = None
        st.session_state["usuario_nome"] = ""
        st.session_state["usuario_perfil"] = ""
        st.rerun()
# ==========================================

st.markdown("""
    <style>
    .card-anuncio {
        background-color: #1e1e1e;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    .btn-whatsapp {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 6. SUAS PÁGINAS E PARTE DINÂMICA (SUAS REGRA DE NEGÓCIO)
# ==========================================
if pagina_selecionada == "🏠 Home":
    st.markdown("# 🎁 Vantagens Exclusivas")

    # Buscar dados do banco (mantendo a sua lógica de conexão)
    parceiros_ativos = []
    try:
        conn = criar_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        hoje_str = datetime.now().strftime('%Y-%m-%d')
        # Ajuste a consulta se necessário para garantir que pega a logo
        cursor.execute("SELECT * FROM stories_parceiros WHERE status_anuncio = 'ativo' AND data_vencimento >= %s", [hoje_str])
        parceiros_ativos = cursor.fetchall()
    except Exception as e:
        st.error(f"Erro ao carregar parceiros: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    # --- 2. Seção de Stories (TOP) ---
    if parceiros_ativos:
        titulos_abas = [f'🏟️ {p["nome_parceiro"]}' for p in parceiros_ativos]
        Abas = st.tabs(titulos_abas)
        
        for i, p in enumerate(parceiros_ativos):
            with Abas[i]:
                # Logo e Nome no topo
                col_logo, col_nome = st.columns([1, 4])

                caminho_logo = os.path.join("media", p["url_logo"])
                if os.path.exists(caminho_logo):
                    st.image(caminho_logo, width=70)
                else:
                    st.markdown("🏟️")
                with col_nome:
                    st.markdown(f"### **{p['nome_parceiro']}**")
                
                # Imagem Principal grande (do jeito que você gosta)
                if p.get("imagem_story"):
                    try:
                        st.image(p["imagem_story"], use_container_width=True)
                    except:
                        st.info("Imagem indisponível")
                
                # Texto abaixo da imagem
                st.write(p.get("texto_story", ""))
                
                # Botão de contato (o que funcionava bem)
                if p.get("link_cupom"):
                    st.link_button("📱 Entrar em Contato", p["link_cupom"], use_container_width=True)
    else:
        st.info("Nenhum parceiro no momento.")

    
    # --- ÁREA DE POSTAGEM ---
    st.subheader("📝 Criar Publicação")

    with st.expander("Clique aqui para postar algo novo"):
        # Mantido fora do form para evitar travamentos de upload no Streamlit
        upload_arquivo = st.file_uploader("Foto ou Vídeo:", type=["png", "jpg", "jpeg", "mp4"])
        
        with st.form("form_postagem", clear_on_submit=True):
            texto_post = st.text_area("O que você está pensando?", height=100)
            btn_postar = st.form_submit_button("Publicar no Mural")
            
            if btn_postar:
                # 1. Validação básica
                if not texto_post and upload_arquivo is None:
                    st.warning("Escreva algo ou anexe uma mídia para postar!")
                else:
                    # Valor padrão para caso não haja arquivo
                    nome_arquivo = None 

                    # 2. SE HOUVER ARQUIVO, PROCESSA O NOME E SALVA
                    if upload_arquivo is not None:
                        nome_original = upload_arquivo.name.lower()
                        # Limpeza do nome
                        nome_arquivo = nome_original.replace(" ", "_")
                        nome_arquivo = nome_arquivo.replace("(", "").replace(")", "")
                        nome_arquivo = re.sub(r'[^a-z0-9._-]', '', nome_arquivo)

                        st.write(f"DEBUG POSTAGEM: Salvando {nome_arquivo}")
                        
                        # Definição de pastas
                        pasta_do_script = os.path.dirname(os.path.abspath(__file__))
                        pasta_uploads = os.path.join(pasta_do_script, "uploads")
                        
                        if not os.path.exists(pasta_uploads):
                            os.makedirs(pasta_uploads)
                            
                        caminho_completo = os.path.join(pasta_uploads, nome_arquivo)
                        
                        # Salvar arquivo
                        with open(caminho_completo, "wb") as f:
                            f.write(upload_arquivo.getbuffer())
                    
                    # 3. INSERÇÃO NO BANCO
                    conn = criar_conexao()
                    cursor = conn.cursor()
                    sql = "INSERT INTO postagens (username_autor, legenda, url_midia) VALUES (%s, %s, %s)"
                    valores = (st.session_state["usuario_nome"], texto_post, nome_arquivo)
                    
                    cursor.execute(sql, valores)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.success("Postagem realizada com sucesso!")
                    st.rerun()

            
# --- ABAIXO DISSO COMEÇA O SEU MURAL --- 


    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### FEED  DOS ATLETAS")


    # --- CSS CORRIGIDO: Alinhamento preciso e sem quebras no mobile ---
    st.markdown(
        """
        <style>
        /* Container do Post */
        div[data-testid="stVerticalBlock"] > div[className*="stVerticalBlockBorderWrapper"] {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 16px !important;
            padding: 14px !important;
            margin-bottom: 12px !important;
        }

        /* Container flexível para os botões ficarem colados na base */
        .botoes-base-container {
            display: flex;
            gap: 10px; /* Distância exata entre o botão de curtir e comentar (ajuste se quiser mais perto) */
            align-items: center;
            margin-top: 10px;
        }

        /* Estilo dos botões da base (Curtir e Comentar) */
        .botoes-base-container button {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid #334155 !important;
            border-radius: 20px !important;
            padding: 6px 14px !important;
            color: #f1f5f9 !important;
            font-size: 13px !important;
            width: auto !important;
            min-height: 36px !important;
        }

        /* Botão de Excluir (Lixeira) no Topo */
        .lixeira-topo button {
            background-color: transparent !important;
            border: none !important;
            color: #ef4444 !important;
            font-size: 16px !important;
            padding: 4px !important;
            box-shadow: none !important;
            width: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    conn = None
    try:
        conn = criar_conexao()
        df_posts = pd.read_sql("SELECT id_post, username_autor, subtitulo_autor, legenda, curtidas, tipo_midia, url_midia FROM postagens ORDER BY id_post DESC", conn)
        
        if df_posts.empty:
            st.info("Nenhuma publicação no momento. Seja o primeiro!")
        else:
            for _, post in df_posts.iterrows():


                with st.container(border=True):
                    col_id = post['id_post']
                    usuario_atual = st.session_state.get("usuario_nome")
                    is_autor = (post['username_autor'] == usuario_atual)
                    
                    # --- 1. CABEÇALHO (Nome do usuário e Lixeira colada logo ao lado) ---
                    # Usamos colunas bem próximas para a lixeira não fugir para a ponta da tela
                    col_autor, col_lixeira = st.columns([0.8, 0.2]) if is_autor else st.columns([1.0, 0.01])
                    
                    with col_autor:
                        st.markdown(
                            f"""
                            <div style="display: flex; align-items: center; width: 100%;">
                                <div style="background-color: #0f172a; padding: 10px 12px; border-radius: 50%; font-size: 16px; margin-right: 12px; border: 1px solid #334155;">跑</div>
                                <div style="line-height: 1.3;">
                                    <strong style="color: #f8fafc; font-size: 15px; font-weight: 600;">{post['username_autor']}</strong><br>
                                    <span style="color: #10b981; font-size: 11px; font-weight: bold; background: rgba(16,185,129,0.1); padding: 2px 8px; border-radius: 20px; display: inline-block; margin-top: 2px;">{post['subtitulo_autor']}</span>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    
                    if is_autor:
                        with col_lixeira:
                            # Envolvemos na classe CSS para estilizar o botão nativo do Streamlit
                            st.markdown('<div class="lixeira-topo">', unsafe_allow_html=True)
                            if st.button("🗑️", key=f"dl_{col_id}"):
                                try:
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM comentarios WHERE id_post = %s", (col_id,))
                                    cursor.execute("DELETE FROM curtidas_posts WHERE id_post = %s", (col_id,))
                                    cursor.execute("DELETE FROM postagens WHERE id_post = %s", (col_id,))
                                    conn.commit()
                                    cursor.close()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao deletar: {e}")
                            st.markdown('</div>', unsafe_allow_html=True)

                    # --- 2. LEGENDA DO POST ---
                    st.markdown(f"""
                        <div style='color: #e2e8f0; font-size: 14px; line-height: 1.5; margin-top: 14px; margin-bottom: 12px; word-wrap: break-word;'>
                            {post['legenda']}
                        </div>
                    """, unsafe_allow_html=True)


                    # --- 3. CONTEÚDO DE MÍDIA MID-CARD ---
                    if pd.notnull(post['url_midia']) and post['url_midia'].strip() != "":
                        pasta_do_script = os.path.dirname(os.path.abspath(__file__))
                        caminho_completo = os.path.join(pasta_do_script, "uploads", post['url_midia'])
                        tipo_limpo = post['tipo_midia'].lower() if post['tipo_midia'] else ""

                        # 1. Verifica se é uma imagem
                        if any(ext in post['url_midia'].lower() for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                            if os.path.exists(caminho_completo):
                                try:
                                    with open(caminho_completo, "rb") as image_file:
                                        st.image(image_file.read(), use_container_width=True)
                                except Exception as e:
                                    st.error(f"Erro ao carregar imagem: {e}")
                            else:
                                st.warning(f"Arquivo não encontrado: {post['url_midia']}")

                        # 2. Verifica se é um vídeo
                        elif 'video' in tipo_limpo or '🎬' in tipo_limpo:
                            st.video(caminho_completo)

                        # 3. Verifica se é um link
                        elif 'link' in tipo_limpo or '🔗' in tipo_limpo:
                            st.markdown(f"🔗 <a href='{post['url_midia']}' target='_blank' style='color: #10b981; font-weight: bold; text-decoration: none;'>Acessar Link Externo</a>", unsafe_allow_html=True)
                                            

                                        
                    # Botão Curtir
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM curtidas_posts WHERE id_post = %s AND username = %s", (col_id, usuario_atual))
                    ja_curtiu = cursor.fetchone() is not None
                    cursor.close()
                    emoji_curtir = "❤️" if ja_curtiu else "🤍"
                    
                    if st.button(f"{emoji_curtir} {post['curtidas']}", key=f"lk_{col_id}"):
                        cursor = conn.cursor()
                        if ja_curtiu:
                            cursor.execute("DELETE FROM curtidas_posts WHERE id_post = %s AND username = %s", (col_id, usuario_atual))
                            cursor.execute("UPDATE postagens SET curtidas = GREATEST(0, curtidas - 1) WHERE id_post = %s", (col_id,))
                        else:
                            cursor.execute("INSERT INTO curtidas_posts (id_post, username) VALUES (%s, %s)", (col_id, usuario_atual))
                            cursor.execute("UPDATE postagens SET curtidas = curtidas + 1 WHERE id_post = %s", (col_id,))
                        conn.commit()
                        cursor.close()
                        st.rerun()
                    
                    # Botão Comentários
                    texto_coment_botao = "💬 Comentários" if not st.session_state.get(f"ver_comentarios_{col_id}", False) else "🔼 Ocultar"
                    if st.button(texto_coment_botao, key=f"b_cm_{col_id}"):
                        st.session_state[f"ver_comentarios_{col_id}"] = not st.session_state.get(f"ver_comentarios_{col_id}", False)
                        st.rerun()
                        
                    st.markdown('</div>', unsafe_allow_html=True) # Fecha a div dos botões colados
                            
                    # --- 5. ÁREA DE COMENTÁRIOS EXPANSÍVEL ---
                    if st.session_state.get(f"ver_comentarios_{col_id}", False):
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        novo_comentario = st.text_input("Escreva um comentário...", key=f"input_coment_{col_id}", label_visibility="collapsed", placeholder="Escreva um comentário...")
                        if st.button("Enviar", key=f"envia_coment_{col_id}", use_container_width=True):
                            if novo_comentario.strip():
                                cursor = conn.cursor()
                                cursor.execute("INSERT INTO comentarios (id_post, username_autor, texto) VALUES (%s, %s, %s)", 
                                            (col_id, usuario_atual, novo_comentario.strip()))
                                conn.commit()
                                cursor.close()
                                st.rerun()
                                    
                        df_comentarios = pd.read_sql("SELECT username_autor, texto FROM comentarios WHERE id_post = %s ORDER BY id_comentario DESC", conn, params=[col_id])
                                    
                        if df_comentarios.empty:
                            st.caption("Nenhum comentário ainda. Comece a conversa!")
                        else:
                            for _, com in df_comentarios.iterrows():
                                st.markdown(
                                    f"""
                                    <div style="background-color: #0f172a; padding: 10px 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid #1e293b; word-wrap: break-word;">
                                        <strong style="color: #10b981; font-size: 13px;">@{com['username_autor']}</strong>
                                        <p style="color: #cbd5e1; font-size: 13px; margin: 4px 0 0 0;">{com['texto']}</p>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )

                        
                                
    except Exception as e:
        st.error(f"Erro ao carregar o feed: {e}")
    finally:
        if conn:
            conn.close()

elif pagina_selecionada == "🏢 Gerenciar Espaço":
    # 1. Primeiro a verificação de acesso (que já criamos)
    id_dono = st.session_state["id_pelada"] # Certifique-se que o ID está no session_state
    
    if verificar_acesso_quadra(id_dono):
        # 2. SE ESTIVER PAGO, MOSTRA O FORMULÁRIO
        with st.form("cadastro_horario"):
            dia = st.date_input("Data da Pelada")
            horario = st.text_input("Horário")
            valor = st.number_input("Valor")
            descricao = st.text_area("Descrição")
            btn_salvar = st.form_submit_button("Postar Horário")

        # 3. LOGO ABAIXO DO FORMULÁRIO, A LÓGICA DE SALVAMENTO
        if btn_salvar:
            try:
                conn = criar_conexao()
                cursor = conn.cursor()
                
                # O CÓDIGO QUE VOCÊ PERGUNTOU VAI AQUI:
                query = """INSERT INTO horario (id_pelada, dia, horario, valor, descricao) 
                           VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (id_dono, dia, horario, valor, descricao))
                
                conn.commit()
                st.success("Horário postado com sucesso!")
                cursor.close()
                conn.close()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
    else:
        # AVISO DE BLOQUEIO
        st.error("Sua mensalidade está pendente. Regularize para postar.")

elif pagina_selecionada == "🛠️ Painel Admin":
    if perfil_usuario_atual == "admin":
        st.title("🛠️ Painel de Controle Supremo")
        
        # Centralizando tudo em abas
        tab1, tab2, tab3 = st.tabs(["🚀 Anunciantes", "⚽ Donos de Quadra", "📥 Filas de Comprovantes"])
        
        with tab1:
            st.subheader("🚀 Gestão de Anunciantes")
            
            with st.form("form_anunciante"):
                nome = st.text_input("Nome da Empresa")
                logo_url = st.text_input("URL do Logo (Imagem redonda)")
                img_story = st.text_input("URL da Imagem do Anúncio")
                texto = st.text_area("Texto Promocional")
                link = st.text_input("Link do WhatsApp (ex: https://wa.me/...)")
                semanas = st.number_input("Duração (Semanas)", min_value=1, max_value=4, value=1)
                
                btn_enviar = st.form_submit_button("Cadastrar Anunciante")
                
                if btn_enviar:
                    # Lógica para salvar no banco (ajuste conforme seu banco)
                    # A data_vencimento agora é calculada: hoje + (semanas * 7 dias)
                    data_venc = (datetime.now() + timedelta(weeks=semanas)).strftime('%Y-%m-%d')
                    
                    # Aqui entraria seu cursor.execute com os dados...
                    st.success(f"Anunciante {nome} cadastrado até {data_venc}!")
            
        with tab2:
            st.subheader("Gestão de Donos de Quadra")
            # Aqui vai a lista de quadras com a lógica de 30 dias
            # Colocaremos o botão de liberar que criamos
            
            try:
                conn = criar_conexao()
                cursor = conn.cursor()
                
                # TESTE 1: Verificar se o comando está chegando no banco
                cursor.execute("SELECT id_pelada, nome, status_pagamento, data_vencimento_mensalidade FROM peladas")
                quadras = cursor.fetchall()
                
                # TESTE 2: Avisar na tela se o banco voltou vazio
                if not quadras:
                    st.write("DEBUG: O banco retornou 0 resultados para a tabela 'peladas'.")
                else:
                    st.write(f"DEBUG: Encontrei {len(quadras)} quadras.")
                    
                    for q in quadras:
                        col1, col2, col3 = st.columns([3, 2, 1])
                        col1.write(f"**{q['nome']}**")
                        col2.write(f"Status: {q['status_pagamento']} | Vence: {q['data_vencimento_mensalidade']}")
                        
                        if col3.button("✅ Liberar 30 dias", key=f"lib_{q['id_pelada']}"):
                            nova_data = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                            cursor.execute("""
                                UPDATE peladas 
                                SET status_pagamento = 'pago', 
                                    data_vencimento_mensalidade = %s 
                                WHERE id_pelada = %s
                            """, (nova_data, q['id_pelada']))
                            conn.commit()
                            st.success(f"Acesso de {q['nome']} renovado!")
                            st.rerun()
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                st.error(f"Erro ao conectar ou ler banco: {e}")

        with tab3:
            st.subheader("📥 Comprovantes Pendentes")
            conn = criar_conexao()
            # Busca todas as solicitações pendentes
            df_solicitacoes = pd.read_sql("SELECT * FROM solicitacoes_pagamento WHERE status = 'Pendente'", conn)
            
            if not df_solicitacoes.empty:
                for _, sol in df_solicitacoes.iterrows():
                    with st.container(border=True):
                        st.write(f"**Quadra:** {sol['nome_usuario']}")
                        # Aqui o Streamlit já entende o caminho 'uploads/foto.jpg'
                        st.image(sol['caminho_comprovante'], width=300) 
                        
                        if st.button(f"✅ Aprovar {sol['nome_usuario']}", key=f"apv_{sol['id']}"):
                    # ... [Seu código de UPDATE na tabela usuarios aqui]
                            # 1. Libera 30 dias no seu sistema (exemplo adaptado ao seu código)
                            nova_data = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE usuarios SET data_expiracao = %s WHERE id_usuario = %s", (nova_data, sol['id_usuario']))
                            # 2. Marca a solicitação como aprovada
                            cursor.execute("UPDATE solicitacoes_pagamento SET status = 'Aprovado' WHERE id = %s", (sol['id'],))
                            conn.commit()
                            registrar_notificacao(sol['id_usuario'], "Parabéns! Seu pagamento foi confirmado e seu acesso liberado por 30 dias.")
                            st.success(f"Aprovado! Notificação enviada para {sol['nome_usuario']}.")
                            st.rerun()
            else:
                st.info("Nenhum comprovante pendente.")
            conn.close()        

elif pagina_selecionada == "⚽ Clubes":
    exibir_aba_clubes()

elif pagina_selecionada == "👤 Meu Perfil":
    exibir_perfil()

elif pagina_selecionada == "🏃 Boleiros":
    exibir_aba_boleiros()

elif pagina_selecionada == "🏟️ Quadras":
    exibir_aba_quadras()

elif pagina_selecionada == "🔔 Notificações":
    exibir_aba_notificacoes()

elif pagina_selecionada == "🔍 Buscar":
    st.title("🔍 Central de Busca & Novidades")
    st.markdown("Encontre atletas, peladas ou confira o que os clubes e arenas estão postando agora.")
    
    # Abas principais da tela de busca
    abas_busca = st.tabs(["🏃 Atletas / Boleiros", "⚽ Peladas / Rachas", "🛡️ Clubes"])

   
    with abas_busca[0]:
        st.subheader("🔎 Filtrar Atletas")
        
        # Campo de busca por nome (ocupa a linha inteira)
        busca_nome_atleta = st.text_input("Buscar Atleta pelo Nome", placeholder="Digite o nome do jogador...", key="busca_nom_atleta")
        
        # Filtros listados sequencialmente (Garante 100% de responsividade no celular sem quebrar)
        busca_posicao = st.selectbox("Filtrar por Posição", ["Todos", "Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Ponta", "Centroavante"], key="busca_pos_atleta")
        
        busca_cidade = st.text_input("Filtrar por Cidade", placeholder="Ex: São Paulo", key="busca_cid_atleta")
        
        busca_overall = st.slider("Rating Mínimo (Overall)", 1, 99, 50, key="busca_ovr_atleta")
            
        # Botão largo ocupando a tela inteira para clique fácil
        if st.button("🔍 Aplicar Filtros de Atletas", key="btn_busca_atleta", use_container_width=True):
            conn = None
            try:
                conn = criar_conexao()
                query = """
                    SELECT a.nome, a.posicao_principal, a.cidade, a.estado,
                        h.nota_velocidade, h.nota_passe, h.nota_fisico, 
                        h.nota_finalizacao, h.nota_drible, h.nota_defesa
                    FROM atletas a
                    INNER JOIN habilidades_atletas h ON a.id_atleta = h.id_atleta
                    WHERE 1=1
                """
                params = []
                
                # Filtro por Nome (Novo)
                if busca_nome_atleta.strip():
                    query += " AND a.nome LIKE %s"
                    params.append(f"%{busca_nome_atleta.strip()}%")
                # Filtros Antigos Preservados
                if busca_posicao != "Todos":
                    query += " AND a.posicao_principal = %s"
                    params.append(busca_posicao)
                if busca_cidade.strip():
                    query += " AND a.cidade LIKE %s"
                    params.append(f"%{busca_cidade.strip()}%")
                    
                df_busca = pd.read_sql(query, conn, params=params)
                
                if not df_busca.empty:
                    df_busca['overall'] = ((df_busca['nota_velocidade'] + df_busca['nota_passe'] + 
                                            df_busca['nota_fisico'] + df_busca['nota_finalizacao'] + 
                                            df_busca['nota_drible'] + df_busca['nota_defesa']) / 6).astype(int)
                    
                    df_filtrado = df_busca[df_busca['overall'] >= busca_overall]
                    
                    if df_filtrado.empty:
                        st.warning("Nenhum atleta encontrado com esses critérios.")
                    else:
                        st.success(f"Encontramos {len(df_filtrado)} atleta(s)!")
                        for _, atleta in df_filtrado.iterrows():
                            with st.container(border=True):
                                col_txt, col_ovr = st.columns([4, 1])
                                with col_txt:
                                    st.markdown(f"### **{atleta['nome']}**")
                                    st.markdown(f"⚽ Posição: `{atleta['posicao_principal']}` | 📍 Cidade: {atleta['cidade']}-{atleta['estado']}")
                                with col_ovr:
                                    st.metric(label="RATING", value=atleta['overall'])
                else:
                    st.warning("Nenhum atleta cadastrado com esses critérios.")
            except Exception as e:
                st.error(f"Erro ao buscar atletas: {e}")
            finally:
                if conn and conn.is_connected():
                    conn.close()

    # ==========================================================
    # ABA 2: PELADAS / RACHAS
    # ==========================================================
    with abas_busca[1]:
        st.markdown("### 📰 Ofertas e Horários Recentes")
        
        conn = criar_conexao()
        query = "SELECT * FROM postagens_quadras"
        df_postagens = pd.read_sql(query, conn)
        
        st.markdown("### 🔍 Filtrar Postagens")

        # Cria uma linha com colunas para organizar os filtros
        c1, c2, c3 = st.columns(3)

        with c1:
            filtro_busca = st.text_input("Buscar por Nome ou Endereço da Arena")
        with c2:
            filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos", "Geral", "🔥 Promoção Relâmpago", "⏳ Horário Vago", "Eventos / Torneios"])
        with c3:
            filtro_data = st.date_input("Filtrar por Data", value=None) # Valor None permite não filtrar

        # --- LÓGICA DE FILTRAGEM ---
        df_filtrado = df_postagens.copy() # df_postagens é o que veio do banco

        # Filtro de texto (Nome ou Endereço)
        if filtro_busca:
            df_filtrado = df_filtrado[
                df_filtrado['nome_arena'].str.contains(filtro_busca, case=False, na=False) | 
                df_filtrado['endereco_arena'].str.contains(filtro_busca, case=False, na=False)
            ]

        # Filtro de Tipo
        if filtro_tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['tag_promocao'] == filtro_tipo]

        # Filtro de Data
        if filtro_data:
            # Garante que a coluna de data esteja no formato datetime
            df_filtrado['data_jogo'] = pd.to_datetime(df_filtrado['data_jogo']).dt.date
            df_filtrado = df_filtrado[df_filtrado['data_jogo'] == filtro_data]

        # --- EXIBIÇÃO ---
        if not df_filtrado.empty:
            st.write(f"Encontradas {len(df_filtrado)} postagens:")
            # Aqui vai o seu código que percorre o df_filtrado e mostra os cards
        else:
            st.info("Nenhuma postagem encontrada com estes filtros.")

            
        query = """
            SELECT p.*, pa.nome_alfa, pa.id_alfa 
            FROM postagens_quadras p
            LEFT JOIN peladas_ativas pa ON p.id_pelada_vinculada = pa.id_pelada
            ORDER BY p.id_post DESC
        """
        df_posts = pd.read_sql(query, conn)
        
        if not df_posts.empty:
            for row in df_posts.itertuples():
                with st.container(border=True):
                    # Usamos getattr para evitar erros caso a coluna não exista ou seja None
                    nome_arena = getattr(row, 'nome_arena', 'Arena sem nome')
                    endereco = getattr(row, 'endereco_arena', 'Endereço não informado')
                    
                    st.markdown(f"#### **{nome_arena}**")
                    st.caption(f"📍 {endereco}")
                    
                    st.caption(f"📌 `{getattr(row, 'tag_promocao', 'Geral')}`")
                    st.markdown(getattr(row, 'conteudo', ''))
                    
                    # Exibir data e valor formatados
                    col_info1, col_info2 = st.columns(2)
                    # Verifica se valor é numérico antes de formatar
                    valor = float(row.valor) if row.valor is not None else 0.0
                    col_info1.info(f"📅 Dados: {row.data_jogo}")
                    col_info2.info(f"💵 Valor: R$ {valor:.2f}")
                    
                    # VERIFICAÇÃO DO ALFA
                    # Verifica se o campo não é NaN (nulo)
                    if not pd.isna(row.id_pelada_vinculada):
                        # Trata os valores None/NaN do JOIN
                        id_alfa = row.id_alfa if row.id_alfa is not None else 0
                        nome_alfa = row.nome_alfa if row.nome_alfa is not None else "Aguardando Organizador"
                        
                        if id_alfa == 0 or nome_alfa == "Aguardando Organizador":
                            if st.button("👑 Assumir como Boleiro Alfa", key=f"btn_{row.id_post}"):
                                cursor = conn.cursor()
                                cursor.execute("UPDATE peladas_ativas SET nome_alfa = %s, id_alfa = %s WHERE id_pelada = %s", 
                                (st.session_state["usuario_nome"], st.session_state["usuario_id"], row.id_pelada_vinculada))
                                conn.commit()
                                cursor.close()
                                st.rerun()
                        else:
                            st.success(f"🏃‍♂️ Organizado por: {nome_alfa}")
    

    with abas_busca[2]:
        st.markdown("### 📰 Publicações Recentes")
        
        conn = None
        try:
            conn = criar_conexao()
            # 🔄 Buscando as novas colunas de contato do banco
            query = """
            SELECT nome_clube, conteudo, tag_aviso, zap_contato, email_contato, 
                nome_arquivo_media, TO_CHAR(data_postagem, 'YYYY-MM-DD') as data 
            FROM postagens_clubes 
            ORDER BY data_postagem DESC
            """
            df_posts = pd.read_sql(query, conn)
            
            if not df_posts.empty:
                for idx, post in df_posts.iterrows():
                    with st.container(border=True):
                        st.markdown(f"#### **{post['nome_clube']}**")
                        st.caption(f"📌 Tipo: `{post['tag_aviso']}`")
                        
                        st.markdown(post['conteudo'])
                        st.write("") 

                        nome_midia = post.get('nome_arquivo_media')
                        nome_midia_str = str(nome_midia) if nome_midia is not None else ""

                        if nome_midia_str and nome_midia_str != "nan" and nome_midia_str.strip() != "":
                            caminho = os.path.join("media", nome_midia_str)
                            
                            if os.path.exists(caminho):
                                if nome_midia_str.lower().endswith(('.mp4', '.mov')):
                                    st.video(caminho)
                                else:
                                    st.image(caminho, use_container_width=True)
                                                
                        texto_whatsapp = "📱 Chamar no WhatsApp"
                        texto_email = "✉️ Enviar E-mail"
                        if "amistoso" in post['conteudo'].lower() or "desafio" in post['conteudo'].lower():
                            texto_whatsapp = "⚔️ Aceitar Desafio (WhatsApp)"
                            texto_email = "⚔️ Aceitar Desafio (E-mail)"
                        elif "peneira" in post['conteudo'].lower() or "vaga" in post['conteudo'].lower():
                            texto_whatsapp = "📋 Candidatar-se via WhatsApp"
                            texto_email = "📋 Enviar Currículo por E-mail"
                        
                        # 🔄 LÓGICA DE EXIBIÇÃO DOS BOTÕES COM FOCO MOBILE
                        tem_zap = post['zap_contato'] and str(post['zap_contato']).strip() != ""
                        tem_email = post['email_contato'] and str(post['email_contato']).strip() != ""
                        
                        # Se tiver WhatsApp, renderiza o botão de link direto
                        if tem_zap:
                            # Remove caracteres do número caso o usuário digite com traço ou parênteses
                            num_limpo = "".join(filter(str.isdigit, str(post['zap_contato'])))
                            # Texto pré-definido para facilitar a vida do usuário no celular
                            mensagem_pronta = f"Olá! Vi a sua publicação do {post['nome_clube']} no app NextDraft e fiquei interessado."
                            link_zap = f"https://wa.me/{num_limpo}?text={mensagem_pronta.replace(' ', '%20')}"
                            
                            st.link_button(texto_whatsapp, link_zap, use_container_width=True)
                        
                        # Se tiver E-mail, renderiza o botão de e-mail (mailto)
                        if tem_email:
                            email_limpo = str(post['email_contato']).strip()
                            assunto_pronto = f"Contato via NextDraft - {post['nome_clube']}"
                            link_email = f"mailto:{email_limpo}?subject={assunto_pronto.replace(' ', '%20')}"
                            
                            st.link_button(texto_email, link_email, use_container_width=True)
                        
                        # --- RODAPÉ DE CONTATO SECUNDÁRIO (Texto de segurança) ---
                        if tem_email or tem_zap:
                            contatos_texto = []
                            if tem_zap: contatos_texto.append(f"WhatsApp: {post['zap_contato']}")
                            if tem_email: contatos_texto.append(f"E-mail: {post['email_contato']}")
                            st.caption(f"📞 Contato direto: {' | '.join(contatos_texto)}")
                            
                        data_formatada = post.get('data', 'Data não disponível')
                        st.caption(f"🕒 Publicado em: {data_formatada}")
                                            
            else:
                st.info("Nenhum clube postou no mural ainda. Seja o primeiro!")
                
        except Exception as e:
            st.error(f"Erro ao carregar o mural dos clubes: {e}")
        finally:
            if conn:
                conn.close()

elif pagina_selecionada == "💬 Chat":
    st.markdown("### 💬 Suas Conversas & Grupos") 
    st.caption("Combine os detalhes das partidas no grupo do racha ou negocie direto no privado.") 
    
    id_usuario_atual = int(st.session_state.get("usuario_id"))
    nome_usuario_atual = st.session_state.get("usuario_nome")
    
    # =====================================================================
    # 1. BUSCA DE USUÁRIO PARA CHAT PRIVADO
    # =====================================================================
    st.markdown("#### 🔍 Iniciar Conversa Privada")
    busca_nome = st.text_input("Digite o nome do boleiro:", key="busca_usuario_chat")
    
    if busca_nome.strip():
        conn = None
        try:
            conn = criar_conexao()
            query_busca = "SELECT id_usuario, username, tipo_perfil FROM usuarios WHERE username LIKE %s AND id_usuario != %s LIMIT 5"
            df_busca = pd.read_sql(query_busca, conn, params=[f"%{busca_nome.strip()}%", id_usuario_atual])
            
            if not df_busca.empty:
                opcoes_busca = {f"✨ Conversar com: {r['username']} ({r['tipo_perfil']})": r for _, r in df_busca.iterrows()}
                usuario_encontrado = st.selectbox("Selecione o usuário:", ["-- Clique para escolher --"] + list(opcoes_busca.keys()), key="resultado_busca_chat")
                
                if usuario_encontrado != "-- Clique para escolher --":
                    dados_novos = opcoes_busca[usuario_encontrado]
                    st.session_state["chat_ativo_id"] = dados_novos['id_usuario']
                    st.session_state["chat_ativo_nome"] = dados_novos['username']
                    st.session_state["chat_tipo"] = "privado"
                    st.rerun()
        finally:
            if conn and conn.is_connected(): conn.close()

    st.markdown("---")

    # =====================================================================
    # 2. CARREGAR CONVERSAS ATIVAS (GRUPOS E PRIVADAS)
    # =====================================================================
    opcoes_chat = {}
    conn = None
    try:
        conn = criar_conexao()
        
        # A. GRUPOS (APENAS ONDE O USUÁRIO ESTÁ CONFIRMADO)
        query_grupos = """
            SELECT DISTINCT p.id_pelada, p.nome_jogo, p.nome_arena, p.id_alfa
            FROM peladas_ativas p
            INNER JOIN escalacao_pelada e ON p.id_pelada = e.id_pelada
            WHERE (e.id_jogador = %s OR p.id_alfa = %s) 
              AND e.status_vaga = 'Confirmado'
        """
        df_grupos = pd.read_sql(query_grupos, conn, params=[id_usuario_atual, id_usuario_atual])
        for _, grp in df_grupos.iterrows():
            chave = f"🏟️ GRUPO: {grp['nome_jogo']} ({grp['nome_arena']})"
            opcoes_chat[chave] = {"id": grp['id_pelada'], "nome": grp['nome_jogo'], "tipo": "grupo", "id_alfa": grp['id_alfa']}

        # B. PRIVADAS
        query_todos = """
            SELECT DISTINCT u.id_usuario, u.username, u.tipo_perfil 
            FROM usuarios u
            INNER JOIN mensagens_chat m ON (u.id_usuario = m.id_envia OR u.id_usuario = m.id_recebe)
            WHERE (m.id_envia = %s OR m.id_recebe = %s) AND u.id_usuario != %s
               AND (m.id_pelada IS NULL OR m.id_pelada = 0)
        """
        df_todos = pd.read_sql(query_todos, conn, params=[id_usuario_atual, id_usuario_atual, id_usuario_atual])
        for _, c in df_todos.iterrows():
            chave = f"👤 {c['username']} ({c['tipo_perfil']})"
            opcoes_chat[chave] = {"id": c['id_usuario'], "nome": c['username'], "tipo": "privado"}
            
    except Exception as e:
        st.error(f"Erro ao carregar contatos: {e}")
    finally:
        if conn: 
            conn.close()

    # Seletor
    selecionado = st.selectbox("📱 Escolha uma conversa:", ["-- Selecione --"] + list(opcoes_chat.keys()))
    if selecionado != "-- Selecione --":
        chat_dados = opcoes_chat[selecionado]
        st.session_state["chat_ativo_id"] = chat_dados['id']
        st.session_state["chat_ativo_nome"] = chat_dados['nome']
        st.session_state["chat_tipo"] = chat_dados['tipo']
        st.session_state["chat_alfa_id"] = chat_dados.get('id_alfa', 0)

    st.markdown("---")

    # =====================================================================
    # 3. JANELA DE CHAT (HISTÓRICO COM DESTAQUE PARA ALFA)
    # =====================================================================
    cid = st.session_state.get("chat_ativo_id")
    nome = st.session_state.get("chat_ativo_nome")
    tipo = st.session_state.get("chat_tipo", "privado")
    alfa_id = st.session_state.get("chat_alfa_id", 0)

    if cid and nome:
        st.markdown(f"#### {'🏟️ Grupo' if tipo == 'grupo' else '🗣️ Conversa'}: {nome}")
        
        conn = None
        try:
            conn = criar_conexao()
            # Carregar histórico
            if tipo == "grupo":
                query_hist = "SELECT id_envia, nome_envia, mensagem FROM mensagens_chat WHERE id_pelada = %s ORDER BY data_envio ASC"
                df_chat = pd.read_sql(query_hist, conn, params=[cid])
            else:
                query_hist = "SELECT id_envia, nome_envia, mensagem FROM mensagens_chat WHERE ((id_envia=%s AND id_recebe=%s) OR (id_envia=%s AND id_recebe=%s)) AND (id_pelada IS NULL OR id_pelada=0) ORDER BY data_envio ASC"
                df_chat = pd.read_sql(query_hist, conn, params=[id_usuario_atual, cid, cid, id_usuario_atual])
            
            with st.container(height=300, border=True):
                for _, msg in df_chat.iterrows():
                    if int(msg['id_envia']) == id_usuario_atual:
                        with st.chat_message("user"):
                            st.write(msg['mensagem'])
                    else:
                        # Lógica da Coroa: Se for grupo e o id_envia for igual ao id_alfa, coroa!
                        avatar = "👑" if (tipo == "grupo" and int(msg['id_envia']) == int(alfa_id)) else "⚽"
                        with st.chat_message("assistant", avatar=avatar):
                            if tipo == "grupo": st.markdown(f"**{msg['nome_envia']}**")
                            st.write(msg['mensagem'])
                            
            resposta = st.chat_input("Digite sua mensagem...")
            if resposta:
                cursor = conn.cursor()
                if tipo == "grupo":
                    cursor.execute("INSERT INTO mensagens_chat (id_envia, nome_envia, id_pelada, id_recebe, mensagem) VALUES (%s, %s, %s, 0, %s)", (id_usuario_atual, nome_usuario_atual, cid, resposta))
                else:
                    cursor.execute("INSERT INTO mensagens_chat (id_envia, nome_envia, id_recebe, id_pelada, mensagem) VALUES (%s, %s, %s, 0, %s)", (id_usuario_atual, nome_usuario_atual, cid, resposta))
                conn.commit()
                st.rerun()
        finally:
            if conn and conn.is_connected(): conn.close()
# ==========================================

