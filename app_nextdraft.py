import streamlit as st
import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente escondidas no arquivo .env
load_dotenv()

# Configuração da página da Web (Título que aparece na aba do navegador)
st.set_page_config(page_title="NextDraft - Scouting", page_icon="⚽", layout="wide")

# Título Principal do Dashboard
st.title("⚽ NextDraft - Plataforma de Inteligência de Mercado")
st.markdown("---")

# 1. Função para buscar os dados no MySQL
@st.cache_data  # Faz o app carregar mais rápido guardando os dados na memória
def carregar_dados_scout():
    # 🔒 SEGURANÇA MÁXIMA: Puxando os dados direto do arquivo oculto .env
    conexao = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    query_sql = """
    SELECT 
        atletas.nome,
        atletas.posicao_principal AS posicao,
        atletas.estado,
        historico_desempenho.partidas_jogadas AS partidas,
        historico_desempenho.gols_marcados AS gols,
        historico_desempenho.nota_velocidade AS velocidade,
        historico_desempenho.nota_finalizacao AS finalizacao
    FROM atletas
    INNER JOIN historico_desempenho 
        ON atletas.id_atleta = historico_desempenho.id_atleta;
    """
    df = pd.read_sql(query_sql, conexao)
    conexao.close()
    
    # Adicionando nossas métricas avançadas que a comissão técnica adora
    df["gols_por_partida"] = (df["gols"] / df["partidas"]).fillna(0)
    df["indice_eficiencia"] = (df["velocidade"] * 0.4) + (df["finalizacao"] * 0.6)
    
    return df

try:
    dados = carregar_dados_scout()

    # -----------------------------------------------------------------
    # 🎛️ FILTROS INTERATIVOS (Painel Lateral)
    # -----------------------------------------------------------------
    st.sidebar.header("🔍 Filtros de Busca")
    
    # Filtro 1: Seleção de Posição (Pega as posições únicas do banco automaticamente)
    todas_posicoes = ["Todas"] + list(dados["posicao"].unique())
    posicao_selecionada = st.sidebar.selectbox("Escolha a Posição:", todas_posicoes)
    
    # Filtro 2: Velocidade Mínima (Slider Corrigido: vai de 0 a 100, começa no 50)
    velocidade_minima = st.sidebar.slider("Velocidade Mínima (Nota):", 0, 100, 50)

    # Aplicando os filtros escolhidos pelo usuário no DataFrame do Pandas
    dados_filtrados = dados[dados["velocidade"] >= velocidade_minima]
    if posicao_selecionada != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados["posicao"] == posicao_selecionada]

    # -----------------------------------------------------------------
    # 📊 EXIBIÇÃO DOS COMPONENTES VISUAIS
    # -----------------------------------------------------------------
    
    # Criando cartões com os principais destaques (KPIs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🏃 Total de Atletas Filtrados", value=len(dados_filtrados))
    with col2:
        st.metric(label="🎯 Média de Eficiência", value=f"{dados_filtrados['indice_eficiencia'].mean():.1f}")
    with col3:
        # Mostra o nome do jogador mais veloz baseado nos filtros
        if not dados_filtrados.empty:
            veloz = dados_filtrados.loc[dados_filtrados["velocidade"].idxmax()]["nome"]
            st.metric(label="⚡ Jogador Mais Veloz do Filtro", value=veloz)
        else:
            st.metric(label="⚡ Jogador Mais Veloz do Filtro", value="Nenhum")

    st.markdown("### 📋 Tabela Geral de Monitoramento")
    # Versão atualizada sem avisos chatos no terminal (usando width='stretch')
    st.dataframe(dados_filtrados.sort_values(by="indice_eficiencia", ascending=False), width="stretch")

    # Criando um gráfico visual de barras para comparar o total de gols
    st.markdown("### ⚽ Análise Comparativa de Gols Marcados")
    if not dados_filtrados.empty:
        st.bar_chart(data=dados_filtrados, x="nome", y="gols")
    else:
        st.warning("Nenhum atleta corresponde aos filtros selecionados para gerar o gráfico.")

except Exception as erro:
    st.error(f"Erro ao carregar o dashboard: {erro}")