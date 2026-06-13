import mysql.connector
import pandas as pd

print("📊 [NextDraft - Inteligência de Mercado] Iniciando Análise Avançada...")
print("=====================================================================")

try:
    # 1. Conexão com o Banco de Dados
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Melao123!",  # 💻 COLOQUE SUA SENHA DO MYSQL AQUI!
        database="nextdraft"
    )

    if conexao.is_connected():
        # Query trazendo os dados para o cálculo de performance
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
        
        # Carrega os dados no DataFrame do Pandas
        df = pd.read_sql(query_sql, conexao)
        
        # -----------------------------------------------------------------
        # 🧠 ENGENHARIA DE RECURSOS (Métricas que clubes de futebol usam)
        # -----------------------------------------------------------------
        
        # Métrica 1: Média de Gols por Partida (G/P)
        df["gols_por_partida"] = df["gols"] / df["partidas"]
        # Preenche com 0 caso algum atleta não tenha jogado nenhuma partida (evita erro de divisão por zero)
        df["gols_por_partida"] = df["gols_por_partida"].fillna(0)
        
        # Métrica 2: Índice de Eficiência Ofensiva (Média ponderada entre Velocidade e Finalização)
        # Clubes criam índices para achar "pechinchas" ou talentos escondidos nas categorias de base
        df["indice_eficiencia"] = (df["velocidade"] * 0.4) + (df["finalizacao"] * 0.6)
        
        # Ordena a tabela para destacar os jogadores mais eficientes no topo
        df_ranking = df.sort_values(by="gols_por_partida", ascending=False)
        
        print("\n📈 RANKING DE PERFORMANCE DOS ATLETAS (Ordenado por Gols/Partida):")
        # Mostrando colunas específicas e formatando a visualização
        print(df_ranking[["nome", "posicao", "partidas", "gols", "gols_por_partida", "indice_eficiencia"]])
        print("---------------------------------------------------------------------")
        
        # -----------------------------------------------------------------
        # 💾 EXPORTAÇÃO AUTOMÁTICA PARA EXCEL
        # -----------------------------------------------------------------
        nome_arquivo = "Relatorio_Scouting_NextDraft.xlsx"
        
        # O Pandas cria o arquivo Excel sozinho com os dados calculados!
        df_ranking.to_excel(nome_arquivo, index=False, sheet_name="Ranking Performance")
        
        print(f"✨ Sucesso! O arquivo '{nome_arquivo}' foi gerado na pasta do seu projeto.")
        print("📁 Você já pode abri-lo no Excel para enviar à comissão técnica!")

        conexao.close()

except Exception as erro:
    print(f"❌ Falha ao processar inteligência de mercado: {erro}")

print("=====================================================================")