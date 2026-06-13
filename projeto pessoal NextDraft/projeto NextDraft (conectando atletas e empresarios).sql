USE nextdraft;


DROP TABLE IF EXISTS historico_desempenho;
DROP TABLE IF EXISTS atletas;
DROP TABLE IF EXISTS usuarios;


CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(300) NOT NULL,
    email VARCHAR(300) NOT NULL UNIQUE,
    senha VARCHAR(300) NOT NULL,
    tipo_usuario ENUM('treinador_escolinha', 'olheiro_empresario') NOT NULL,
    status_assinatura ENUM('gratuito', 'premium') DEFAULT 'gratuito',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE atletas (
    id_atleta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario_criador INT NOT NULL,
    nome VARCHAR(300) NOT NULL,
    data_nascimento DATE NOT NULL,
    posicao_principal ENUM ('goleiro', 'zagueiro', 'lateral direito', 'lateral esquerdo', 'primeiro volante', 'segundo volante', 'meio campo', 'ponta esquerda', 'ponta direita', 'centro avante') NOT NULL,
    perna_preferida ENUM ('canhoto', 'destro', 'ambidestro'),
    altura_cm INT NOT NULL,
    peso_kg DECIMAL(5,2) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    FOREIGN KEY (id_usuario_criador) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE historico_desempenho (
    id_registro INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    id_atleta INT NOT NULL,
    periodo VARCHAR(300) NOT NULL,
    partidas_jogadas INT DEFAULT 0,
    gols_marcados INT DEFAULT 0,
    assistencia INT DEFAULT 0,
    cartoes_amarelos INT DEFAULT 0,
    cartoes_vermelhos INT DEFAULT 0,
    nota_velocidade INT DEFAULT 60,
    nota_passe INT DEFAULT 60,
    nota_fisico INT DEFAULT 60,
    nota_finalizacao INT DEFAULT 60,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_atleta) REFERENCES atletas(id_atleta) ON DELETE CASCADE
);


-- 2. Insere o Usuário (Lucas Olheiro) - Ele receberá o ID 1 automaticamente
INSERT INTO usuarios (id_usuario, nome_usuario, email, senha, tipo_usuario, status_assinatura)
VALUES (1, 'Lucas Olheiro', 'lucas@olheiro.com', 'senha123', 'olheiro_empresario', 'premium');

-- 3. Insere os dois Atletas vinculados ao Lucas (id_usuario_criador = 1)
INSERT INTO atletas (id_atleta, id_usuario_criador, nome, data_nascimento, posicao_principal, perna_preferida, altura_cm, peso_kg, cidade, estado)
VALUES 
(1, 1, 'Pedrinho Malandrinha', '2010-05-14', 'ponta direita', 'destro', 165, 58.50, 'São Paulo', 'SP'),
(2, 1, 'Thiaguinho Paredão', '2009-11-22', 'zagueiro', 'canhoto', 182, 74.00, 'Rio de Janeiro', 'RJ'),
(3,1, 'carlos mandrake', '2007-02-14', 'lateral', 'destro', 190, 75.00, 'sao paulo', 'sp');

-- 4. Insere o Histórico de Desempenho (As notas estilo FIFA) de cada um deles
INSERT INTO historico_desempenho (id_atleta, periodo, partidas_jogadas, gols_marcados, assistencia, nota_velocidade, nota_passe, nota_fisico, nota_finalizacao)
VALUES 
(1, 'Temporada Atual 2026', 12, 8, 5, 88, 75, 68, 82), -- Notas do Pedrinho (id_atleta = 1)
(2, 'Temporada Atual 2026', 15, 1, 0, 62, 70, 85, 45); -- Notas do Thiaguinho (id_atleta = 2)



SELECT 
    atletas.nome AS nome_do_jogador,
    atletas.posicao_principal AS posicao,
    historico_desempenho.nota_velocidade AS velocidade,
    historico_desempenho.nota_finalizacao AS finalizacao,
    historico_desempenho.gols_marcados AS gols
FROM atletas
INNER JOIN historico_desempenho 
    ON atletas.id_atleta = historico_desempenho.id_atleta
WHERE atletas.posicao_principal = 'ponta direita' 
  AND historico_desempenho.nota_velocidade >= 80;
  

USE nextdraft;

SELECT 
    atletas.estado AS Estado,
    COUNT(atletas.id_atleta) AS Total_Jogadores,
    AVG(atletas.altura_cm) AS Media_Altura_CM,
    SUM(historico_desempenho.gols_marcados) AS Total_Gols_Marcados
FROM atletas
INNER JOIN historico_desempenho 
    ON atletas.id_atleta = historico_desempenho.id_atleta
GROUP BY atletas.estado;

USE nextdraft;


SELECT 
    atletas.nome AS nome_do_jogador,
    atletas.posicao_principal AS posicao,
    historico_desempenho.gols_marcados AS gols
FROM atletas
INNER JOIN historico_desempenho 
    ON atletas.id_atleta = historico_desempenho.id_atleta
ORDER BY historico_desempenho.gols_marcados DESC
LIMIT 3;




