import mysql.connector

# --- PASSO 1: A FUNÇÃO DE ANÁLISE (CÉREBRO DO PYTHON) ---
def classificar_velocidade(nota):
    if nota >= 80:
        return "💎 ATLETA DE ELITE (Enviar para o Real Madrid)"
    elif nota >= 70:
        return "🚀 PROMISSOR (Monitorar de perto)"
    else:
        return "🌱 EM DESENVOLVIMENTO (Treino de base)"

print("🔄 Conectando ao Banco de Dados e Gerando Relatório...")
print("==========================================================")

try:
    # --- PASSO 2: CONEXÃO REAL COM O MYSQL ---
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Melao123!",  # 💻 COLOQUE SUA SENHA DO MYSQL AQUI!
        database="nextdraft"
    )

    if conexao.is_connected():
        cursor = conexao.cursor(dictionary=True)
        
        # Query com INNER JOIN para pegar os dados cadastrais E as notas de velocidade
        query_sql = """
        SELECT 
            atletas.nome,
            atletas.posicao_principal,
            historico_desempenho.nota_velocidade
        FROM atletas
        INNER JOIN historico_desempenho 
            ON atletas.id_atleta = historico_desempenho.id_atleta;
        """
        
        cursor.execute(query_sql)
        atletas_do_banco = cursor.fetchall()

        # --- PASSO 3: O LOOP AUTOMATIZADO ---
        for atleta in atletas_do_banco:
            nome = atleta["nome"]
            posicao = atleta["posicao_principal"]
            velocidade = atleta["nota_velocidade"] # Dado real vindo do INNER JOIN!

            # Python usa a função para decidir o status do jogador do banco
            status_scout = classificar_velocidade(velocidade)

            # Print indentado (com Tab) para mostrar um por um na tela
            print(f"🏃 Atleta: {nome}")
            print(f"📊 Posição: {posicao} | Velocidade: {velocidade}")
            print(f"🎯 Veredito: {status_scout}")
            print("----------------------------------------------------------")

        # Fechando os acessos
        cursor.close()
        conexao.close()

except Exception as erro:
    print(f"❌ Falha no sistema: {erro}")

print("==========================================================")
print("📊 Relatório finalizado com sucesso!")