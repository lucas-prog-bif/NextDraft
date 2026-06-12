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



insert into usuarios ( nome_usuario, email, senha, tipo_usuario, status_assinatura) values 
('carlos', 'carlossilva@gameil.com', 4523654 , 'treinador_escolinha', 'gratuito');

insert into atletas ( id_usuario_criador, nome, data_nascimento, posicao_principal, perna_preferida, altura_cm, peso_kg, cidade, estado) values
(1, 'carlos', '2008-10-19', 'centro avante', 'canhoto', 1.64, 75.56, 'sao paulo', 'sp');

select * from atletas;