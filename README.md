NextDraft - Plataforma de Inteligência de Mercado & Scouting
Bem-vindo ao NextDraft ! Este projeto é um MVP de nível industrial e pessoal focado no departamento de análise de mercado e scouting de clubes de futebol profissional. O sistema foi desenvolvido para centralizar dados brutos de atletas, calcular estatísticas de desempenho e entregar relatórios visuais interativos para a comissão técnica e diretores de futebol. Unindo atleta, clube e empresário, buscando um modelo preditivo para analisar futuras e gerar oportunidades.

Para que serve este projeto?
Eu construí um pipeline de dados completo de ponta a ponta:

Armazenei os dados estruturados dos atletas (finalização, passe e etc...) em um banco de dados relacional.
Conectei o Python ao banco para extrair e tratar essas informações com segurança.
Analisei o desempenho criando indicadores de desempenho (KPIs) usados ​​por analistas reais de clubes.
Entreguei os resultados de duas formas: um relatório automatizado em Excel e um painel (Dashboard) interativo na Web.
Arquitetura do Sistema e Tecnologias
O projeto foi dividido em camadas para garantir escalabilidade e segurança:

Banco de Dados (MySQL): Armazenamento seguro de dados usando chaves primárias/estranhas e restrições de integridade ( ENUM).
Processamento e Análise (Python & Pandas): Engenharia de recursos para cálculo de médias, somas e rankings de eficiência.
Interface Visual (Streamlit): Transformação do código analítico em um painel web interativo com gráficos e filtros em tempo real.
Segurança (Python-Dotenv): Isolamento de credenciais confidenciais (senhas do banco) fora do código-fonte.
Passo a Passo do Desenvolvimento
Módulo 1: Modelagem do Banco (MySQL)
Crie o banco de dados nextdraftcom tabelas interligadas para evitar duplicidade e garantir a integridade dos dados:

usuarios: Guarda quem está usando o sistema (ex: Olheiros, Empresários).
atletas: Guarda a ficha cadastral básica do jogador (Nome, Posição Principal, Perna, Estado de Origem). Aqui uso o tipo ENUMpara trabalhar como cargos oficiais do futebol e evitar erros de digitação.
historico_desempenho: Conectada à tabela de atletas via chave estrangeira ( FOREIGN KEY). Guarda os dados de jogos, gols e os atributos físicos e técnicos.
Nota para me lembrar: Usei o comando COMMIT;no MySQL Workbench para garantir que as alterações feitas na mão fossem salvas no disco e ficassem visíveis para o Python.

Módulo 2: Integração e Escrita (Python + mysql-connector)
Desenvolvi scripts ( teste.pye cadastrar_atleta.py) para abrir conexões com o servidor local.
Para inserir novos atletas diretamente pelo Python, utilize placeholders ( %s) . Isso impede ataques de SQL Injection , garantindo que o texto digitado seja tratado como dado, e não como comando conformevel.
Usei o método conexao.commit()no Python para validar a escrita no banco.
Módulo 3: Engenharia de Recursos e Análise ( Pandas)
No arquivo scout_avancado.py, eu ensinei o Pandas a ler nossa consulta do MySQL como INNER JOINe transformá-la em um DataFrame . Saí do básico e criei duas atualizações de mercado:

Gols por Partida: df["gols"] / df["partidas"] -> Identifica a consistência do atacante.
Índice de Eficiência Ofensiva: Uma média ponderada atribuindo peso de 40% para a Velocidade e 60% para a Finalização do atleta, ajudando a encontrar talentos ocultos.
Exportação: Usei o método df.to_excel()com o motor openpyxlpara gerar um relatório .xlsxpronto para ser enviado por e-mail para a diretoria.
Módulo 4: Dashboard Interativo ( Streamlit)
No arquivo app_nextdraft.py, criei uma interface visual do sistema.

Use componentes de tela como st.sidebar.selectbox(filtros de posição), st.sidebar.slider(filtro de velocidade mínima) e st.metricpara exibir cartões de destaque em destaque.
Criei sons sonoros usando st.bar_chartque se adaptam instantaneamente conforme o olheiro mexe nos filtros da tela.
Boas Práticas de Segurança Aplicadas
Para não exportar a senha do banco de dados ao subir o projeto no GitHub, utilize a biblioteca python-dotenv:

As senhas ficam salvas localmente no arquivo .env.
O arquivo .envfoi adicionado dentro do .gitignore, garantindo que ele nunca suba para o repositório público.
Sem código, o acesso é feito via os.getenv("DB_PASSWORD").
Como Rodar o Projeto na Minha Máquina
Ativar o Banco: Verifique se o servidor do MySQL está rodando e com as tabelas povoadas.
Configurar as Senhas: Verifique se o arquivo .envestá na raiz com as credenciais corretas.
Rodar o Dashboard Web: Abra o terminal na pasta do projeto e execute:
python -m streamlit run app_nextdraft.py
