-- 1. CRIAÇÃO DO BANCO DE DADOS
CREATE DATABASE nextdraft;
USE nextdraft;



-- Força o salvamento automático para não perder os dados ao fechar
SET autocommit = 1;

-- 2. REMOÇÃO DE TABELAS ANTIGAS (Para evitar conflitos de estrutura)
DROP TABLE IF EXISTS comentarios;
DROP TABLE IF EXISTS curtidas_posts;
DROP TABLE IF EXISTS postagens;
DROP TABLE IF EXISTS usuarios;

-- ========================================================
-- 3. CRIAÇÃO DAS TABELAS
-- ========================================================

-- 1. Garante que a tabela de parceiros/stories tenha controle de pagamento
ALTER TABLE stories_parceiros ADD COLUMN status_anuncio VARCHAR(20) DEFAULT 'ativo'; -- 'ativo' ou 'vencido'
ALTER TABLE stories_parceiros ADD COLUMN data_vencimento DATE;
ALTER TABLE stories_parceiros ADD COLUMN tipo_plano VARCHAR(50); -- 'quadra_mensal' ou 'destaque_semanal'

-- 2. Se você tiver uma tabela separada para os usuários/donos de quadra, adicione também:
ALTER TABLE usuarios ADD COLUMN tipo_perfil VARCHAR(20) DEFAULT 'jogador'; -- 'jogador', 'dono_quadra', 'admin'

select * from stories_parceiros;


-- Tabela de Usuários
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    perfil_tipo VARCHAR(20) NOT NULL, -- 'atleta', 'peladeiro', 'quadra', 'admin'
    subtitulo_autor VARCHAR(100)
);

-- Tabela de Postagens (Estilo Instagram)
CREATE TABLE postagens (
    id_post INT AUTO_INCREMENT PRIMARY KEY,
    username_autor VARCHAR(50) NOT NULL,
    subtitulo_autor VARCHAR(100),
    url_avatar VARCHAR(255),
    url_imagem VARCHAR(255),
    legenda TEXT,
    curtidas INT DEFAULT 0,
    FOREIGN KEY (username_autor) REFERENCES usuarios(nome_usuario) ON DELETE CASCADE
);

-- Tabela de Controle de Curtidas (Para o usuário não curtir o mesmo post várias vezes)
CREATE TABLE curtidas_posts (
    id_curtida INT AUTO_INCREMENT PRIMARY KEY,
    id_post INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_post) REFERENCES postagens(id_post) ON DELETE CASCADE,
    FOREIGN KEY (username) REFERENCES usuarios(nome_usuario) ON DELETE CASCADE,
    UNIQUE KEY uq_curtida (id_post, username)
);

-- Tabela de Comentários
CREATE TABLE comentarios (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    id_post INT NOT NULL,
    username_autor VARCHAR(50) NOT NULL,
    texto TEXT NOT NULL,
    id_comentario_pai INT DEFAULT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_post) REFERENCES postagens(id_post) ON DELETE CASCADE,
    FOREIGN KEY (username_autor) REFERENCES usuarios(nome_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_comentario_pai) REFERENCES comentarios(id_comentario) ON DELETE CASCADE
);

-- ========================================================
-- 4. INSERÇÃO DOS DADOS DE TESTE (POPULANDO O BANCO)
-- ========================================================

-- Cadastrando o seu usuário como ATLETA e com a senha limpa '123'
INSERT INTO usuarios (nome_usuario, email, senha, perfil_tipo, subtitulo_autor)
VALUES ('lucas_atleta', 'lucas@email.com', '123', 'atleta', '🏃 Meia-Atacante | 17 anos');

-- Cadastrando outros usuários fictícios para interagir no feed
INSERT INTO usuarios (nome_usuario, email, senha, perfil_tipo, subtitulo_autor)
VALUES 
('ney_da_varzea', 'ney@email.com', '123', 'peladeiro', '⚽ Camisa 10 do Resenha FC'),
('arena_lapa', 'lapa@email.com', '123', 'quadra', '🏟️ Zona Oeste - SP');

-- Criando postagens de teste para o Feed carregar imagens reais do Unsplash
INSERT INTO postagens (username_autor, subtitulo_autor, url_avatar, url_imagem, legenda, curtidas)
VALUES 
(
    'ney_da_varzea', 
    '⚽ Camisa 10 do Resenha FC', 
    'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100', 
    'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=600', 
    'Mais uma vitória pro campeonato do final de semana! O elenco tá voando alto e focado na taça! 🏆⚽ #Varzea #FutebolDeRua', 
    14
),
(
    'arena_lapa', 
    '🏟️ Zona Oeste - SP', 
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100', 
    'https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=600', 
    'Horários de terça e quinta à noite com 20% de desconto para quem fechar mensalistas essa semana! Garanta o racha do seu time! 🏟️🔥', 
    8
);

-- 5. CONFIRMAÇÃO SALVAMENTO DEFINITIVO
COMMIT;

USE nextdraft;

CREATE TABLE IF NOT EXISTS comentarios_posts (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    id_post INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    comentario TEXT NOT NULL,
    id_resposta INT DEFAULT NULL, -- Se for preenchido, indica que é uma resposta a outro comentário
    curtidas INT DEFAULT 0,
    fixado TINYINT(1) DEFAULT 0, -- 0 para normal, 1 para fixado pelo dono do post
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_post) REFERENCES postagens(id_post) ON DELETE CASCADE,
    FOREIGN KEY (id_resposta) REFERENCES comentarios_posts(id_comentario) ON DELETE CASCADE
);

-- Tabela auxiliar para controlar quem já curtiu qual comentário (evita curtidas infinitas)
CREATE TABLE IF NOT EXISTS curtidas_comentarios (
    id_curtida INT AUTO_INCREMENT PRIMARY KEY,
    id_comentario INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_comentario) REFERENCES comentarios_posts(id_comentario) ON DELETE CASCADE
);

rename table nome_usuario to username;

USE nextdraft;

-- Rodar esses comandos para adicionar os novos campos caso não existam
ALTER TABLE usuarios ADD COLUMN  url_avatar VARCHAR(255) DEFAULT 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150';
ALTER TABLE usuarios ADD COLUMN  biografia TEXT DEFAULT NULL;
ALTER TABLE usuarios ADD COLUMN  posicao VARCHAR(50) DEFAULT 'Não Informada';
ALTER TABLE usuarios ADD COLUMN  time_coracao VARCHAR(100) DEFAULT 'Não Informado';

DESCRIBE usuarios;

show tables;

-- 1. Criar a tabela principal de Atletas
CREATE TABLE IF NOT EXISTS atletas (
    id_atleta INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_nascimento DATE,
    posicao_principal VARCHAR(50),
    perna_preferida VARCHAR(20),
    altura_cm INT,
    peso_kg DECIMAL(5,2),
    cidade VARCHAR(100),
    estado CHAR(2),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Criar a tabela de atributos técnicos (ligada à tabela de atletas)
CREATE TABLE IF NOT EXISTS habilidades_atletas (
    id_habilidade INT AUTO_INCREMENT PRIMARY KEY,
    id_atleta INT NOT NULL,
    nota_velocidade INT DEFAULT 60,
    nota_passe INT DEFAULT 60,
    nota_fisico INT DEFAULT 60,
    nota_finalizacao INT DEFAULT 60,
    nota_defesa INT DEFAULT 60,
    nota_drible INT DEFAULT 60,
    gols_marcados INT DEFAULT 0,
    assistencias INT DEFAULT 0,
    partidas_jogadas INT DEFAULT 0,
    FOREIGN KEY (id_atleta) REFERENCES atletas(id_atleta) ON DELETE CASCADE
);


 CREATE TABLE IF NOT EXISTS postagens_clubes (
    id_post INT AUTO_INCREMENT PRIMARY KEY,
    nome_clube VARCHAR(100) NOT NULL,
    conteudo TEXT NOT NULL,
    tag_aviso VARCHAR(50) DEFAULT 'Geral', -- Ex: Peneira, Amistoso, Aviso
    data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS postagens_quadras (
    id_post INT AUTO_INCREMENT PRIMARY KEY,
    nome_arena VARCHAR(100) NOT NULL,
    conteudo TEXT NOT NULL,
    tag_promocao VARCHAR(50) DEFAULT 'Geral', -- Ex: Promoção, Horário Vago, Aviso
    data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1. Tabela Principal da Pelada Ativa
CREATE TABLE IF NOT EXISTS peladas_ativas (
    id_pelada INT AUTO_INCREMENT PRIMARY KEY,
    nome_jogo VARCHAR(100) NOT NULL,
    nome_arena VARCHAR(100) NOT NULL,
    endereco_arena VARCHAR(255) NOT NULL,
    data_hora DATETIME NOT NULL,
    id_alfa INT NOT NULL, -- ID do Boleiro organizador (usuário logado)
    nome_alfa VARCHAR(100) NOT NULL,
    max_linha_por_time INT DEFAULT 5, -- Ex: Futebol de 5, 6, 7
    valor_pix DECIMAL(10,2) DEFAULT 0.00,
    chave_pix VARCHAR(100),
    status_jogo VARCHAR(20) DEFAULT 'Aberto' -- Aberto, Lotado, Finalizado
);

-- 2. Tabela de Vagas/Escalação do Campinho
CREATE TABLE IF NOT EXISTS escalacao_pelada (
    id_escalacao INT AUTO_INCREMENT PRIMARY KEY,
    id_pelada INT NOT NULL,
    id_jogador INT NOT NULL,
    nome_jogador VARCHAR(100) NOT NULL,
    overall_jogador INT DEFAULT 60,
    time_escalado VARCHAR(10) NOT NULL, -- 'A', 'B' ou 'RESERVA'
    posicao_quadra VARCHAR(20) NOT NULL, -- 'Goleiro', 'Linha', 'Reserva'
    status_vaga VARCHAR(20) DEFAULT 'Pendente', -- 'Pendente' (esperando o Alfa) ou 'Confirmado'
    FOREIGN KEY (id_pelada) REFERENCES peladas_ativas(id_pelada) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notificacoes (
    id_notificacao INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario_destino INT NOT NULL, -- Para quem vai a mensagem (ID do Atleta, Clube ou Quadra)
    mensagem VARCHAR(255) NOT NULL,
    tipo_alerta VARCHAR(50) DEFAULT 'info', -- 'sucesso', 'aviso', 'info'
    lida BOOLEAN DEFAULT FALSE,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vamos inserir duas notificações de teste para o seu usuário (ID 99)
-- assim a aba já abre com conteúdo real para você testar o visual!
INSERT INTO notificacoes (id_usuario_destino, mensagem, tipo_alerta) VALUES 
(99, '⚽ O Boleiro Alfa aceitou sua solicitação! Você está confirmado no racha de terça.', 'sucesso'),
(99, '⭐ Seu Card recebeu uma nova avaliação e seu Overall subiu!', 'info');

-- Tabela para armazenar as mensagens do chat privado
CREATE TABLE IF NOT EXISTS mensagens_chat (
    id_mensagem INT AUTO_INCREMENT PRIMARY KEY,
    id_envia INT NOT NULL, -- ID de quem mandou a mensagem
    nome_envia VARCHAR(100) NOT NULL,
    id_recebe INT NOT NULL, -- ID de quem vai receber
    mensagem TEXT NOT NULL,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserindo uma mensagem de teste para o seu usuário (ID 99) ver o chat funcionando
INSERT INTO mensagens_chat (id_envia, nome_envia, id_recebe, mensagem) 
VALUES (1, 'Diretor Real Matismo', 99, 'Fala Lucas, curti seu card de Meia. Tá a fim de jogar um amistoso com a gente este final de semana?');

ALTER TABLE postagens ADD COLUMN tipo_midia VARCHAR(20) DEFAULT 'texto'; -- 'texto', 'imagem', 'video', 'link'
ALTER TABLE postagens ADD COLUMN url_midia TEXT DEFAULT NULL;

select * from comentarios_posts;

-- 1. Remove a chave estrangeira antiga que está errada
ALTER TABLE comentarios DROP FOREIGN KEY comentarios_ibfk_2;

-- 2. Cria a chave estrangeira nova apontando para a coluna correta ('username')
ALTER TABLE comentarios 
ADD CONSTRAINT fk_username_autor 
FOREIGN KEY (username_autor) REFERENCES usuarios(username) ON DELETE CASCADE;

describe usuarios;

