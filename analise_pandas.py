import mysql.connector
import pandas as pd  # Por convenção, a comunidade sempre chama o pandas de 'pd'

print("📊 Carregando dados do NextDraft para Análise Estatística...")
print("==========================================================")

try:
    # 1. Conexão padrão com o banco
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Melao123!",  # 💻 COLOQUE SUA SENHA DO MYSQL AQUI!
        database="nextdraft"
    )

    if conexao.is_connected():
        # Query avançada juntando atletas e seus desempenhos históricos
        query_sql = """
        SELECT 
            atletas.nome,
            atletas.posicao_principal AS posicao,
            atletas.altura_cm,
            atletas.peso_kg,
            atletas.estado,
            historico_desempenho.partidas_jogadas AS partidas,
            historico_desempenho.gols_marcados AS gols,
            historico_desempenho.nota_velocidade AS velocidade
        FROM atletas
        INNER JOIN historico_desempenho 
            ON atletas.id_atleta = historico_desempenho.id_atleta;
        """
        
        # 2. O Pandas lê a query e a conexão e cria o DataFrame magicamente!
        df = pd.read_sql(query_sql, conexao)
        
        # --- EXIBIÇÃO DE CIÊNCIA DE DADOS ---
        print("\n👀 Visualizando a Tabela Estruturada (DataFrame):")
        print(df)
        print("----------------------------------------------------------")
        
        # 3. Calculando Insights Prontos na Hora
        print("\n📈 INSIGHTS DA EQUIPE DE SCOUT:")
        
        media_altura = df["altura_cm"].mean()
        total_gols = df["gols"].sum()
        jogador_mais_rapido = df.loc[df["velocidade"].idxmax()]
        
        print(f"🔹 Altura Média do Elenco: {media_altura:.2f} cm")
        print(f"🔹 Total de Gols Marcados na Temporada: {total_gols} gols")
        print(f"🔹 Jogador Mais Veloz Rastreado: {jogador_mais_rapido['nome']} (Nota: {jogador_mais_rapido['velocidade']})")
        
        # Fechando a conexão
        conexao.close()

except Exception as erro:
    print(f"❌ Erro na análise de dados: {erro}")

print("==========================================================")