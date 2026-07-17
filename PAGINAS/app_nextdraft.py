import mysql.connector
import os
import dotenv

# Carrega as variáveis do arquivo .env
dotenv.load_dotenv()

def criar_conexao():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database="nextdraft"
    )