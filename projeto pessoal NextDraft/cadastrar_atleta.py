import mysql.connector

print("📝 Iniciando Sistema de Cadastro de Atletas...")
print("==========================================================")

# 1. Coletando os dados do novo jogador (Simulando o treinador digitando no app)
nome_novo = "Rodrygo Raio"
data_nasc_nova = "2008-01-10"
posicao_nova = "ponta esquerda"
perna_nova = "destro"
altura_nova = 174
peso_novo = 66.00
cidade_nova = "Santos"
estado_nova = "SP"

try:
    # 2. Conectando ao banco de dados
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Melao123!",  # 💻 SUA SENHA AQUI!
        database="nextdraft"
    )

    if conexao.is_connected():
        cursor = conexao.cursor()

        # 3. Preparando o comando SQL com placeholders (%s) por segurança
        comando_insert = """
        INSERT INTO atletas (id_usuario_criador, nome, data_nascimento, posicao_principal, perna_preferida, altura_cm, peso_kg, cidade, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Juntamos os dados na mesma ordem dos %s lá de cima
        # Usamos o id_usuario_criador = 1 (que é o Lucas Olheiro)
        dados_atleta = (1, nome_novo, data_nasc_nova, posicao_nova, perna_nova, altura_nova, peso_novo, cidade_nova, estado_nova)

        # 4. Executando o comando no banco
        cursor.execute(comando_insert, dados_atleta)

        # ✨ A REGRA DE OURO: Lembra do COMMIT que conversamos? No Python ele é OBRIGATÓRIO!
        conexao.commit()

        print(f"✅ Atleta '{nome_novo}' cadastrado com sucesso no MySQL!")

        # Fechando as conexões
        cursor.close()
        conexao.close()

except Exception as erro:
    print(f"❌ Erro ao tentar cadastrar o atleta: {erro}")

print("==========================================================")