##Projeto de Reservas de Veículos##
Este é um projeto de reserva de veículos construído com Python, utilizando a biblioteca Streamlit para a interface web e SQLite para o banco de dados.

#Índice#
Descrição do Projeto
Funcionalidades
Instalação
Como Usar
Como Contribuir
Licença
#Descrição do Projeto#
Este projeto foi desenvolvido para facilitar a gestão de reservas de veículos para uma frota. Ele permite aos usuários fazer login, cadastrar reservas, visualizar reservas existentes e cancelar reservas, tudo em uma interface web amigável.

Funcionalidades
Autenticação de usuários: Permite que apenas colaboradores logados possam fazer e visualizar suas reservas.
Cadastro e visualização de reservas: Os usuários podem cadastrar uma reserva para um veículo e visualizá-las de forma interativa.
Cancelamento de reservas: Apenas o usuário que fez a reserva pode cancelá-la.
Notificações por e-mail: Confirmações de reserva são enviadas por e-mail.
Instalação
Siga os passos abaixo para configurar o projeto localmente:

Pré-requisitos
Certifique-se de ter o Python 3.7+ instalado em sua máquina.
Passos de Instalação
Clone o repositório:

bash
Copiar código
git clone https://github.com/seu-usuario/projeto-reservas.git
cd projeto-reservas
Crie um ambiente virtual:

bash
Copiar código
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Instale as dependências necessárias:

bash
Copiar código
pip install -r requirements.txt
Execute o projeto:

bash
Copiar código
streamlit run app.py
Acesse a aplicação no navegador:

arduino
Copiar código
http://localhost:8501
Como Usar
Login: Ao iniciar a aplicação, você será solicitado a fazer login usando seu e-mail e senha. Apenas usuários com e-mails do domínio "vilaurbe.com.br" são permitidos.

Cadastro: Caso ainda não tenha uma conta, você pode se registrar. Apenas colaboradores da VilaUrbe podem acessar.

Realizar Reservas: Escolha a data e hora de retirada e devolução do veículo, bem como o destino e o carro. O sistema verificará a disponibilidade do veículo antes de concluir a reserva.

Visualizar Reservas: Os usuários podem visualizar suas reservas e cancelá-las.

Como Contribuir
Sinta-se à vontade para contribuir com o projeto! Para isso:

Faça um fork do repositório.
Crie uma branch para suas alterações:
bash
Copiar código
git checkout -b minha-feature
Faça suas mudanças e crie commits.
Envie sua branch para o repositório:
bash
Copiar código
git push origin minha-feature
Abra um Pull Request explicando as mudanças.
Licença
Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

Explicação do Código
Importações de Bibliotecas
Streamlit: Biblioteca usada para criar a interface web do projeto.
Pandas: Utilizado para manipulação de dados.
SQLite: Sistema de banco de dados relacional embutido no Python.
smtplib: Usado para enviar notificações por e-mail.
AgGrid: Biblioteca para criar uma tabela interativa para exibir reservas.
Random e String: Utilizados para gerar tokens aleatórios, como no caso da recuperação de senha.
Estrutura do Código
Conexão com Banco de Dados:

python
Copiar código
conn = sqlite3.connect('reservas.db')
cursor = conn.cursor()
O banco de dados reservas.db é criado ou conectado automaticamente usando SQLite.

Autenticação e Sessão:

O sistema mantém o estado de autenticação dos usuários usando variáveis de sessão (st.session_state).
Funcionalidades de Login e Cadastro:

O sistema de autenticação é baseado na verificação de e-mail e senha com o banco de dados.
Hash de Senha: As senhas são armazenadas usando o algoritmo de hash SHA-256 para segurança.
Reserva de Veículos:

O sistema permite que os usuários reservem veículos escolhendo a data e hora de retirada e devolução.
As reservas são armazenadas no banco de dados e notificações são enviadas por e-mail.
Envio de E-mails:

Para enviar e-mails de confirmação de reserva ou recuperação de senha, a função smtplib é usada para se conectar a um servidor SMTP.
Tabela de Reservas:

A biblioteca AgGrid é usada para exibir uma tabela interativa das reservas existentes. O usuário pode selecionar uma reserva para cancelá-la.
