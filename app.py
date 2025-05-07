import streamlit as st
import pandas as pd
from datetime import datetime, time
import pymysql
import hashlib
import smtplib
import os
import base64
from email.mime.text import MIMEText
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random
import string
import warnings


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'dataurbe.bd')


# Conectar ao banco MySQL
conn = pymysql.connect(
    host='vudw.ddns.net',
    user='vudw',
    password='Vilaurbe#2025!',
    database='dataurbe',
    cursorclass=pymysql.cursors.DictCursor
)



# Configurações gerais
st.set_page_config(layout='wide', page_title="Frota Vilaurbe", page_icon=":car:")
warnings.filterwarnings("ignore", message="Please replace st.experimental_get_query_params with st.query_params.")



# Inicialização de variáveis de sessão
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'login'
if 'reservas' not in st.session_state:
    st.session_state.reservas = []
if 'atualizar_tabela' not in st.session_state:
    st.session_state.atualizar_tabela = False
if 'nome_completo' not in st.session_state:
    st.session_state.nome_completo = None
    
    
# Função para carregar reservas do banco de dados com caching
@st.cache_data
def carregar_reservas_do_banco():
    """Carrega as reservas do banco de dados com caching para melhorar a performance."""
    try:
        # Conectar ao banco MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            return pd.read_sql_query('SELECT * FROM reservas', conn)
    except Exception as e:
        st.error(f'Erro ao carregar reservas: {e}')
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

# Função para limpar o cache de dados
def limpar_cache():
    """Limpa o cache de todas as funções decoradas com @st.cache_data."""
    st.cache_data.clear()
    st.success("Cache limpo com sucesso!")

# Função para gerar um token aleatório    
def gerar_token_tamanho_aleatorio(tamanho=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))    

# Função para criar as tabelas no banco de dados
def criar_tabelas():
    try:
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                nome_completo VARCHAR(255),
                                email VARCHAR(255) UNIQUE,
                                senha VARCHAR(255),
                                token VARCHAR(255)
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS reservas (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                nome_completo VARCHAR(255),
                                email_usuario VARCHAR(255),
                                dtRetirada DATE,
                                hrRetirada TIME,
                                dtDevolucao DATE,
                                hrDevolucao TIME,
                                carro VARCHAR(255),
                                cidade VARCHAR(255),
                                status VARCHAR(50)
                            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                email VARCHAR(255),
                                token VARCHAR(255),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (email) REFERENCES usuarios(email)
                            )''')
            conn.commit()
    except Exception as e:
        st.error(f"Erro ao criar tabelas: {e}")
        
# Função para adicionar um novo usuário
# Função para adicionar um novo usuário
def adicionar_usuario(nome_completo, email, senha):
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    try:
        # Conectar ao banco MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO usuarios (nome_completo, email, senha) VALUES (%s, %s, %s)', 
                           (nome_completo, email, senha_hash))
            conn.commit()
    except Exception as e:
        st.error(f'Erro ao adicionar usuário: {e}')

        
        

# Função para verificar o usuário
def verificar_usuario(email, senha):
    # Verifica se o email tem o domínio correto
    if not email.endswith('@vilaurbe.com.br'):
        st.error("Acesso restrito. Apenas colaboradores são permitidos.")
        return False
    
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    try:
        # Conectar ao banco MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT nome_completo, email FROM usuarios WHERE email = %s AND senha = %s', (email, senha_hash))
            usuario = cursor.fetchone()
            if usuario:
                st.session_state.usuario_logado = usuario['email']
                st.session_state.nome_completo = usuario['nome_completo']
                return True
            else:
                return False
    except Exception as e:
        st.error(f"Erro ao verificar o usuário: {e}")
        return False




def enviar_email_recovery(destinatario, link):
    servidor_smtp = 'smtp.office365.com'
    porta = 587
    remetente = 'ti@vilaurbe.com.br'
    senha = 'V1l@Urb3!!51'

    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = 'Frota Vilaurbe - Recuperação de Senha'
        
        corpo_email = f'Acesse o Link a seguir para cadastrar uma nova senha: {link}'
        msg.attach(MIMEText(corpo_email, 'plain'))
        
        with smtplib.SMTP(servidor_smtp, porta) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())

        print("Email enviado com sucesso!")
    except Exception as e:
        print(f'Erro ao enviar email: {e}')
                
        
def resetar_senha():
    st.title('Redefinir Senha')

    # Obtenção dos parâmetros da URL
    params = st.experimental_get_query_params()
    token = params.get('token', [None])[0]
    token = token.strip() if token else None

    if not token:
        st.error("Token inválido ou expirado.")
        return

    try:
        # Conectar ao banco MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM tokens WHERE token = %s', (token,))
            result = cursor.fetchone()

        if result:
            email = result['email']
            st.text_input("E-mail", value=email, disabled=True)

            nova_senha = st.text_input("Nova Senha", type="password", placeholder="Digite sua nova senha")
            confirmar_senha = st.text_input("Confirmar Senha", type="password", placeholder="Confirme sua nova senha")

            if st.button("Redefinir Senha"):
                if nova_senha != confirmar_senha:
                    st.error("As senhas não correspondem.")
                else:
                    if atualizar_senha_com_token(token, nova_senha):
                        st.success("Senha redefinida com sucesso!")
                        st.info("Agora você pode fazer login com sua nova senha.")
        else:
            st.error("Token inválido ou expirado.")
    except Exception as e:
        st.error(f"Erro ao redefinir senha: {e}")



        
        
def atualizar_senha_com_token(token, nova_senha):
    senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
    try:
        # Conectar ao banco MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            cursor = conn.cursor()
            # Atualizar a senha do usuário baseado no token
            cursor.execute('''UPDATE usuarios SET senha = %s 
                              WHERE email = (SELECT email FROM tokens WHERE token = %s)''', 
                           (senha_hash, token))
            # Excluir o token após o uso
            cursor.execute('DELETE FROM tokens WHERE token = %s', (token,))
            conn.commit()

            # Verificar se alguma linha foi afetada (se o token for válido)
            if cursor.rowcount == 0:
                st.error("Token inválido ou expirado.")
                return False

            return True
    except pymysql.Error as e:
        st.error(f"Erro ao atualizar a senha: {e}")
        return False

        
        
def visualizar_reservas():
    st.markdown('<div style="background-color:#f0f2f6;padding:20px;border-radius:8px;">', unsafe_allow_html=True)
    st.subheader('Visualizar Reservas')

    # Formulário para filtrar reservas
    with st.form(key='filtros'):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            dtRetirada = st.date_input('Data de Retirada')
        with col2:
            dtDevolucao = st.date_input('Data de Devolução')
        with col3:
            carro = st.text_input('Carro')
        with col4:
            cidade = st.text_input('Cidade')

        filtro_aplicado = st.form_submit_button('Buscar')

    if filtro_aplicado:
        df_filtrada = buscar_reservas_filtros(dtRetirada, dtDevolucao, carro, cidade)
        if not df_filtrada.empty:
            df_filtrada = criar_df_para_visualizacao(df_filtrada)
            st.write(estilizar_reservas(df_filtrada))
        else:
            st.error('Nenhuma reserva encontrada.')

    st.markdown('</div>', unsafe_allow_html=True)        
        
        
def carregar_reservas_do_banco():
    try:
        # Conectar ao banco MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            return pd.read_sql_query('SELECT * FROM reservas', conn)
    except Exception as e:
        st.error(f'Erro ao carregar reservas: {e}')
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
      
        
        
def logout():
    #Limpa o estado de sessão do usuario
    st.session_state.usuario_logado = None
    st.session_state.pagina = 'login'
    st.success("Você saiu com sucesso")        
    st.rerun() # Força a atualização da página    

# Função de login
def login():
    st.markdown('', unsafe_allow_html=True)
    st.subheader('Login')

    # Usando o form para detectar o "Enter" ou clique
    with st.form(key='login_form', border=False):
        email = st.text_input('E-mail', placeholder='Digite seu e-mail')
        senha = st.text_input('Senha', type='password', placeholder='Digite sua senha')

        # Esse botão será disparado tanto com o clique quanto com "Enter"
        submit_button = st.form_submit_button('Entrar')

    if submit_button:
        if verificar_usuario(email, senha):
            st.session_state.pagina = 'home'
            st.success('Login realizado com sucesso!')
            st.rerun() # Força a atualização da página
        else:
            st.error('E-mail ou senha incorretos.')    
        
        
# Função de cadastro
def cadastro():
    st.markdown('<div style="background-color:#f0f2f6;padding:20px;border-radius:8px;">', unsafe_allow_html=True)
    st.subheader('Cadastro')
    nome_completo = st.text_input('Nome Completo', placeholder='Digite seu nome completo')
    email = st.text_input('E-mail', placeholder='Digite seu e-mail')
    senha = st.text_input('Senha', type='password', placeholder='Digite sua senha')
    confirmar_senha = st.text_input('Confirme a Senha', type='password', placeholder='Confirme sua senha')
    
    if st.button('Cadastrar'):
        if senha == confirmar_senha:
            # Verifica se o e-mail pertence ao domínio vilaurbe.com.br
            if email.endswith('@vilaurbe.com.br'):
                if adicionar_usuario(nome_completo, email, senha):
                    st.success('Cadastro realizado com sucesso!')
                else:
                    st.error('E-mail já cadastrado.')
            else:
                st.error('Somente para colaboradores "vilaurbe" são permitidos.')
        else:
            st.error('As senhas não correspondem.')
    st.markdown('</div>', unsafe_allow_html=True)       
        
        
        
def registrar_reserva(nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status):
    try:
        # Conectar ao banco MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            cursor = conn.cursor()
            # Inserir a reserva no banco de dados
            cursor.execute('''INSERT INTO reservas (nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status))
            conn.commit()

            # Preparar e enviar notificação sobre a reserva
            dados_reserva = f"Nome: {nome_completo}, Email: {email_usuario}, Data Retirada: {dtRetirada}, Data Devolução: {dtDevolucao}, Hora Retirada: {hrRetirada}, Hora Devolução: {hrDevolucao}, Carro: {carro}, Cidade: {cidade}, Status: {status}"
            enviar_notificacao_reserva(dados_reserva)

            print("Reserva registrada e notificação enviada!")
    except Exception as e:
        print(f"Falha ao registrar reserva: {e}")

        
        
        


def registrar_reserva(nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status):
    try:
        # Conectar ao banco MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            cursor = conn.cursor()
            # Inserir a reserva no banco de dados
            cursor.execute('''INSERT INTO reservas (nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status))
            conn.commit()

            # Preparar e enviar notificação sobre a reserva
            dados_reserva = f"Nome: {nome_completo}, Email: {email_usuario}, Data Retirada: {dtRetirada}, Data Devolução: {dtDevolucao}, Hora Retirada: {hrRetirada}, Hora Devolução: {hrDevolucao}, Carro: {carro}, Cidade: {cidade}, Status: {status}"
            enviar_notificacao_reserva(dados_reserva)

            st.success("Reserva registrada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao registrar reserva: {e}")




# Página de criação de reserva pelo administrador
def criar_reserva_admin():
    st.subheader("Criar Reserva (Admin)")
    nome_completo = st.text_input("Nome Completo do Usuário")
    email_usuario = st.text_input("Email do Usuário")
    dtRetirada = st.date_input("Data de Retirada", value=datetime.now().date())
    hrRetirada = st.time_input("Hora de Retirada", value=time(9, 0))
    dtDevolucao = st.date_input("Data de Devolução", value=datetime.now().date())
    hrDevolucao = st.time_input("Hora de Devolução", value=time(17, 0))
    carro = st.selectbox("Carro", ['SWQ1F92 - Versa Advance', 'SVO6A16 - Saveiro', 'GEZ5262 - Nissan SV', 'Mercedes Benz Vito VAN'])
    cidade = st.text_input("Cidade")
    
    if st.button("Criar Reserva"):
        if nome_completo and email_usuario:
            registrar_reserva(nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, "Agendado")
        else:
            st.error("Preencha todos os campos obrigatórios!")        
        
def buscar_reservas():
    try:
        # Conexão com o banco de dados MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            # Consulta SQL para buscar todas as reservas
            query = "SELECT * FROM reservas"
            df_reservas = pd.read_sql_query(query, conn)
        
        return df_reservas
    except Exception as e:
        st.error(f"Erro ao buscar reservas: {e}")
        return pd.DataFrame()  # Retorna DataFrame vazio se houver erro
      
        
        

        
# Função para exportar reservas para CSV
def exportar_reservas_para_csv(df_reservas):
    csv = df_reservas.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Codifica o CSV para base64
    href = f'<a href="data:file/csv;base64,{b64}" download="reservas.csv">Baixar CSV de todas as reservas</a>'
    st.markdown(href, unsafe_allow_html=True)       
               

def exibir_reservas_interativas():
    df_reservas = carregar_reservas_do_banco()
    
    if not df_reservas.empty:
        df_reservas = df_reservas.rename(columns={
            'nome_completo': 'Nome Completo',
            'dtRetirada': 'Data Retirada',
            'hrRetirada': 'Hora Retirada',
            'dtDevolucao': 'Data Devolução',
            'hrDevolucao': 'Hora Devolução',
            'carro': 'Carro',
            'cidade': 'Destino',
            'status': 'Status'
        })

        df_reservas = df_reservas[['id', 'Nome Completo', 'Data Retirada', 'Hora Retirada', 'Data Devolução', 'Hora Devolução', 'Carro', 'Destino', 'Status']]
        df_reservas = df_reservas.sort_values(by='id', ascending=False)

        gb = GridOptionsBuilder.from_dataframe(df_reservas)
        gb.configure_selection(selection_mode="single", use_checkbox=True)
        gb.configure_grid_options(domLayout='normal')  # Ajuste automático de altura
        gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True)  # Permite que as colunas sejam redimensionadas
        gb.configure_column("id", width=55)  # Define a largura das colunas específicas, ajuste conforme necessário
        gb.configure_column("Nome Completo", width=170)
        gb.configure_column("Carro", width=170)
        gb.configure_column("Destino", width=210)
        gb.configure_column("Status", width=100)
        gb.configure_column("Data Retirada", width=88)
        gb.configure_column("Hora Retirada", width=80)
        gb.configure_column("Data Devolução", width=88)
        gb.configure_column("Hora Devolução", width=80)
        grid_options = gb.build()

        grid_response = AgGrid(df_reservas, gridOptions=grid_options, update_mode=GridUpdateMode.SELECTION_CHANGED, key='reservas_grid')
        selected_rows = grid_response.get('selected_rows', [])

        
        # Validar se o usuário selecionou um registro:
        if selected_rows is None:
            pass
        else:
            selected_id = selected_rows.iloc[0,0]
        
            
            
            btnCancelar = st.button('Cancelar', key='bntCancelar')
            
            
            # Exibir o botão de Cancelar
            if btnCancelar:
                if atualizar_status_reserva(selected_id):
                    st.success('Status da reserva alterado com sucesso')
                    
                    # Recarregar os dados atualizados
                    df_reservas = carregar_reservas_do_banco()
                    st.session_state.df_selecao = df_reservas
                else:
                    st.error('Erro ao alterar o status da reserva.')
                    
    else:
        st.warning('Nenhuma reserva selecionada')    
        
        
        

# Função para atualizar a senha do usuário
def atualizar_senha(email, nova_senha):
    senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
    try:
        with pymysql.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE usuarios SET senha = ? WHERE email = ?', (senha_hash, email))
            conn.commit()
            if cursor.rowcount == 0:
                st.error("Nenhum usuário encontrado com o e-mail fornecido.")
                return False
            return True
    except pymysql.Error as e:
        st.error(f"Erro ao atualizar a senha: {e}")
        return False    
        
        

def recuperar_senha(email):
    token = gerar_token_tamanho_aleatorio()
    salvar_token_no_banco(email, token)
    link = f'https://frotavilaurbe.streamlit.app/?token={token}'  # Substitua pelo domínio do seu app
    enviar_email_recovery(email, link)



def salvar_token_no_banco(email, token):
    try:
        # Conexão com o banco de dados MySQL
        with pymysql.connect(
            host='vudw.ddns.net',
            user='vudw',
            password='Vilaurbe#2025!',
            database='dataurbe',
            cursorclass=pymysql.cursors.DictCursor
        ) as conn:
            cursor = conn.cursor()
            # Insere o token no banco de dados
            cursor.execute('''INSERT INTO tokens (email, token) VALUES (%s, %s)''', (email, token))
            conn.commit()
            
    except pymysql.Error as e:
        print(f'Erro ao salvar token no banco de dados: {e}')



def enviar_notificacao_reserva(email_usuario, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, destinos):
    servidor_smtp = 'smtp.office365.com'
    porta = 587
    remetente = 'ti@vilaurbe.com.br'
    senha = 'V1l@Urb3!!51'
    destinatario = 'analytics@vilaurbe.com.br'  # Destinatário da notificação

    # Formatação das datas para o formato DD/MM/YYYY
    dtRetirada_formatada = dtRetirada.strftime('%d/%m/%Y')
    dtDevolucao_formatada = dtDevolucao.strftime('%d/%m/%Y') 

    assunto = 'Nova Reserva Realizada'
    corpo = f"""
    Prezado(a),

    Informamos que uma nova reserva foi realizada com sucesso. Seguem os detalhes da reserva:

    - Nome do Usuário: {email_usuario}
    - Data de Retirada: {dtRetirada_formatada}
    - Hora de Retirada: {hrRetirada.strftime('%H:%M')}
    - Data de Devolução: {dtDevolucao_formatada}
    - Hora de Devolução: {hrDevolucao.strftime('%H:%M')}
    - Veículo: {carro}
    - Destinos: {destinos}

    Atenciosamente,

    Equipe Frota Vilaurbe
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto

        msg.attach(MIMEText(corpo, 'plain'))

        with smtplib.SMTP(servidor_smtp, porta) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
        
        print("Notificação de reserva enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar notificação de reserva: {e}")


# Função para arredondar a hora para o intervalo mais próximo
def arredondar_para_intervalo(time_obj, intervalo_mins=30):
    total_mins = time_obj.hour * 60 + time_obj.minute
    arredondado = round(total_mins / intervalo_mins) * intervalo_mins
    horas = arredondado // 60
    minutos = arredondado % 60
    return time(horas, minutos)


def adicionar_reserva(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, destinos):
    try:
        # Converte a lista de destinos para uma string separada por vírgulas
        destino_str = ', '.join(destinos) if destinos else ''
        
        # Verifica se o veículo está disponível no período
        if veiculo_disponivel(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro):
            # Conexão com o banco de dados MySQL
            with pymysql.connect(
                host='vudw.ddns.net',
                user='vudw',
                password='Vilaurbe#2025!',
                database='dataurbe',
                cursorclass=pymysql.cursors.DictCursor
            ) as conn:
                cursor = conn.cursor()
                # Insere a nova reserva no banco de dados
                cursor.execute('''INSERT INTO reservas 
                                  (nome_completo, email_usuario, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, cidade, status) 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                               (st.session_state.nome_completo, st.session_state.usuario_logado, 
                                dtRetirada.strftime('%Y-%m-%d'), hrRetirada.strftime('%H:%M:%S'), 
                                dtDevolucao.strftime('%Y-%m-%d'), hrDevolucao.strftime('%H:%M:%S'), 
                                carro, destino_str, 'Agendado'))
                conn.commit()

            # Envia uma notificação de reserva
            enviar_notificacao_reserva(st.session_state.nome_completo, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, destino_str)
            st.success("Reserva realizada com sucesso!")
        else:
            st.error("O veículo já está reservado para o período selecionado.")
    
    except pymysql.Error as e:
        st.error(f"Erro ao adicionar reserva: {e}")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")



def liberar_vaga(reserva_id):
    try:
        with pymysql.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM reservas WHERE id = %s', (reserva_id,))
            conn.commit()
            st.success("Vaga liberada com sucesso!")
    except pymysql.Error as e:
        st.error(f"Erro ao liberar vaga: {e}")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")


# Função para estilizar a visualização de reservas com base no status
def estilizar_reservas(df):
    def aplicar_estilo(status):
        if status == 'Agendado':
            return ['background-color: green']*len(df.columns)
        elif status == 'Em andamento':
            return ['background-color: lightblue']*len(df.columns)
        elif status == 'Concluído':
            return ['background-color: lightgreen']*len(df.columns)
        elif status == 'Cancelado':
            return ['background-color: red']*len(df.columns)
        else:
            return ['']*len(df.columns)
    return df.style.apply(lambda x: aplicar_estilo(x['status']), axis=1)        
        
                
# Função para filtrar reservas com base em critérios específicos
def filtrar_reservas(df, dtRetirada=None, dtDevolucao=None, carros=None, cidades=None):
    if dtRetirada:
        df = df[df['dtRetirada'] == pd.Timestamp(dtRetirada).strftime('%d/%m/%Y')]
    
    if dtDevolucao:
        df = df[df['dtDevolucao'] == pd.Timestamp(dtDevolucao).strftime('%d/%m/%Y')]
        
    
    if carros:
        df = df[df['carro'].str.contains('|'.join(carros), case=False, na=False)]
    
    if cidades:
        df = df[df['cidade'].str.contains('|'.join(cidades), case=False, na=False)]
    
    return df        
        
 
# Função para buscar reservas aplicando filtros
def buscar_reservas_filtros(dtRetirada=None, dtDevolucao=None, carros=None, cidade=None):
    df_reservas = carregar_reservas_do_banco()
    return filtrar_reservas(df_reservas, dtRetirada, dtDevolucao, carros, cidade)       
        
        
def criar_df_para_visualizacao(df):
    df['dtRetirada'] = pd.to_datetime(df['dtRetirada'], format='%d/%m/%Y')
    df['dtDevolucao'] = pd.to_datetime(df['dtDevolucao'], format='%d/%m/%Y')
    df['hrRetirada'] = pd.to_datetime(df['hrRetirada'], format='%H:%M:%S').dt.time
    df['hrDevolucao'] = pd.to_datetime(df['hrDevolucao'], format='%H:%M:%S').dt.time
    return df        
        
    
# Função para verificar se o veículo está disponível
def veiculo_disponivel(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro):
    df_reservas = carregar_reservas_do_banco()

    # Convertendo as datas das reservas para o formato datetime.date
    df_reservas['dtRetirada'] = pd.to_datetime(df_reservas['dtRetirada'], format='%d/%m/%Y').dt.date
    df_reservas['dtDevolucao'] = pd.to_datetime(df_reservas['dtDevolucao'], format='%d/%m/%Y').dt.date
    df_reservas['hrRetirada'] = pd.to_datetime(df_reservas['hrRetirada'], format='%H:%M:%S').dt.time
    df_reservas['hrDevolucao'] = pd.to_datetime(df_reservas['hrDevolucao'], format='%H:%M:%S').dt.time

    dtRetirada_date = pd.to_datetime(dtRetirada).date()
    dtDevolucao_date = pd.to_datetime(dtDevolucao).date()

    for index, row in df_reservas.iterrows():
        if row['carro'] == carro and row['status'] != 'Cancelado':
            if dtRetirada_date <= row['dtDevolucao'] and dtDevolucao_date >= row['dtRetirada']:
                if (hrRetirada >= row['hrRetirada'] and hrRetirada <= row['hrDevolucao']) or \
                   (hrDevolucao >= row['hrRetirada'] and hrDevolucao <= row['hrDevolucao']) or \
                   (hrRetirada <= row['hrRetirada'] and hrDevolucao >= row['hrDevolucao']):
                    return False
    return True    
    
    
def enviar_email_cancelamento(destinatario, detalhes_reserva):
    servidor_smtp = 'smtp.office365.com'
    porta = 587
    remetente = 'ti@vilaurbe.com.br'
    senha = 'V1l@Urb3!!51'

    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = 'Notificação de Cancelamento de Reserva'

        corpo_email = f"""
Prezados,

Informamos que a seguinte reserva foi cancelada:

ID da Reserva: {detalhes_reserva['id']}
Nome do Usuário: {detalhes_reserva['nome_completo']}
Email do Usuário: {detalhes_reserva['email_usuario']}
Data de Retirada: {detalhes_reserva['dtRetirada']}
Hora de Retirada: {detalhes_reserva['hrRetirada']}
Data de Devolução: {detalhes_reserva['dtDevolucao']}
Hora de Devolução: {detalhes_reserva['hrDevolucao']}
Carro: {detalhes_reserva['carro']}
Cidade: {detalhes_reserva['cidade']}

Atenciosamente,
Equipe Frota Vilaurbe
"""
        msg.attach(MIMEText(corpo_email, 'plain'))

        with smtplib.SMTP(servidor_smtp, porta) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())

        print(f"Notificação de cancelamento enviada para {destinatario}!")
        st.info(f"Notificação de cancelamento enviada para {destinatario}!") # Feedback visual
    except Exception as e:
        print(f'Erro ao enviar email de cancelamento: {e}')
        st.error(f'Erro ao enviar email de cancelamento: {e}')

def atualizar_status_reserva(selected_id):
    try:
        # Certifique-se de que o selected_id é um número inteiro
        selected_id = int(selected_id)

        # Conectar ao banco de dados
        with pymysql.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Buscar detalhes da reserva ANTES de atualizar o status
            cursor.execute("SELECT * FROM reservas WHERE id = %s", (selected_id,))
            reserva_detalhes = cursor.fetchone()

            if reserva_detalhes:
                colunas = [column[0] for column in cursor.description]
                detalhes_reserva_dict = dict(zip(colunas, reserva_detalhes))
                email_reserva = detalhes_reserva_dict['email_usuario']

                # Verificar se o usuário logado tem permissão para cancelar
                if email_reserva == st.session_state.usuario_logado or st.session_state.usuario_logado == 'analytics@vilaurbe.com.br':
                    # Atualizar o status da reserva para "Cancelado"
                    cursor.execute("UPDATE reservas SET status = 'Cancelado' WHERE id = %s", (selected_id,))
                    conn.commit()
                    st.success('Reserva cancelada com sucesso!')

                    # Enviar notificação por e-mail para analytics@vilaurbe.com.br
                    enviar_email_cancelamento('analytics@vilaurbe.com.br', detalhes_reserva_dict)

                    # Marcar para recarregar a tabela
                    st.session_state.atualizar_tabela = True
                    st.rerun()
                else:
                    st.error('Você não tem permissão para cancelar esta reserva.')
            else:
                st.error('Reserva não encontrada.')

    except pymysql.Error as e:
        st.error(f"Erro ao atualizar o status da reserva: {e}")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")

    

# Função para exibir o botão de exportação apenas para o usuário autorizado
def exibir_importar_reservas():
    # Definir o usuário autorizado para importar
    usuario_autorizado_importar = 'adm02@vilaurbe.com.br'  # Substitua pelo e-mail do admin

    if 'usuario_logado' in st.session_state:
        st.write(f"Usuário logado: {st.session_state.usuario_logado}")  # Debugging

        if st.session_state.usuario_logado == usuario_autorizado_importar:
            st.write('### Importar reservas de CSV:')
            carregar_reservas_do_csv()
        else:
            st.info("Você não tem permissão para importar reservas.")
    else:
        st.write("Nenhum usuário logado.")

def carregar_reservas_do_csv():
    uploaded_file = st.file_uploader("Selecione um arquivo CSV para importar", type=["csv"])
    if uploaded_file is not None:
        try:
            df_importado = pd.read_csv(uploaded_file)
            if st.button("Confirmar Importação", key='confirmar_importacao_button'):
                # Aqui você chamaria a função para salvar os dados do DataFrame no seu banco de dados
                st.success("Reservas importadas com sucesso!")
                st.dataframe(df_importado) # Exibir os dados importados
        except Exception as e:
            st.error(f"Erro ao ler o arquivo CSV: {e}")  
    
def buscar_todas_reservas_do_banco():
    """
    Busca todas as reservas do banco de dados SQLite reservas.db.
    Retorna um DataFrame com todas as reservas.
    """
    try:

        # Conectar ao banco de dados MySQL
        conn = pymysql.connect(
            host='vudw.ddns.net',  # Endereço do servidor MySQL
            user='vudw',            # Usuário do banco de dados
            password='Vilaurbe#2025!',  # Senha do banco de dados
            database='dataurbe',    # Nome do banco de dados
            cursorclass=pymysql.cursors.DictCursor  # Para retornar resultados como dicionários
        )


        query = "SELECT * FROM reservas"  # Supondo que sua tabela de reservas se chama 'reservas'
        df_reservas = pd.read_sql_query(query, conn)
        conn.close()
        return df_reservas
    except pymysql.Error as e:
        st.error(f"Erro ao acessar o banco de dados SQLite: {e}")
        return pd.DataFrame()

def exportar_df_para_csv(df, filename):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )
    
    
def verificar_tabelas():
    try:
        with pymysql.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            st.write('Tabelas existentes:', tables)

            for table_name in [t[0] for t in tables]:
                st.write(f'Colunas da tabela {table_name}:')
                cursor.execute(f"DESCRIBE {table_name};")
                columns = cursor.fetchall()
                for column in columns:
                    st.write(f'  {column[0]}')  # column[0] contém o nome da coluna
    except pymysql.Error as e:
        st.error(f"Erro ao verificar tabelas: {e}")
  
    
    

def home_page():
    criar_tabelas()

    st.sidebar.image('logo.png', use_column_width=True)

    if st.session_state.get('usuario_logado'):
        st.sidebar.header(f'Bem vindo, {st.session_state.nome_completo}')

        #Adicionar botão de logout na barra lateral
        if st.sidebar.button('Logout'):
            logout()
            
            
        # Definir o usuário autorizado para importação
        usuario_autorizado_exportar_tudo = 'analytics@vilaurbe.com.br'  # Substitua pelo e-mail do admin

        # Exibir o botão de importação apenas para o usuário autorizado
        # Exibir o botão de exportação total apenas para o usuário autorizado
        if st.session_state.usuario_logado == usuario_autorizado_exportar_tudo:
            st.subheader("Exportar Todas as Reservas")
            if st.button("Exportar Todas as Reservas para CSV", key='exportar_todas_reservas_button'):
                df_todas_reservas = buscar_todas_reservas_do_banco()
                if not df_todas_reservas.empty:
                    exportar_df_para_csv(df_todas_reservas, 'todas_as_reservas.csv')
                    st.success("Todas as reservas foram exportadas para o arquivo 'todas_as_reservas.csv'.")
                else:
                    st.info("Não há reservas para exportar.")

        with st.container(border=True):
            st.title('Reserva')
            col1, col2 = st.columns(2)

            # Variáveis de controle para confirmação de datas de final de semana
            if 'retirada_confirmada' not in st.session_state:
                st.session_state.retirada_confirmada = False
            if 'devolucao_confirmada' not in st.session_state:
                st.session_state.devolucao_confirmada = False

            with col1:
                dtRetirada = st.date_input(label='Data de Retirada', key='dtRetirada', value=datetime.now(), format='DD/MM/YYYY')
                hrRetirada = st.time_input(label='Hora de Retirada', key='hrRetirada', value=time(9, 0))

                # Verificar se a data de retirada é no final de semana
                if dtRetirada.weekday() >= 5 and not st.session_state.retirada_confirmada:
                    st.warning("A data de retirada é um final de semana. Deseja continuar?")
                    if st.button("Confirmar Retirada", key="confirmar_retirada"):
                        st.session_state.retirada_confirmada = True  # Usuário confirmou a data
                elif dtRetirada.weekday() < 5:
                    # Se for durante a semana, a data é automaticamente confirmada
                    st.session_state.retirada_confirmada = True

            with col2:
                dtDevolucao = st.date_input(label='Data de Devolução', key='dtDevolucao', value=datetime.now(), format='DD/MM/YYYY')
                hrDevolucao = st.time_input(label='Hora de Devolução', key='hrDevolucao', value=time(9, 0))

                # Verificar se a data de devolução é no final de semana
                if dtDevolucao.weekday() >= 5 and not st.session_state.devolucao_confirmada:
                    st.warning("A data de devolução é um final de semana. Deseja continuar?")
                    if st.button("Confirmar Devolução", key="confirmar_devolucao"):
                        st.session_state.devolucao_confirmada = True  # Usuário confirmou a data
                elif dtDevolucao.weekday() < 5:
                    # Se for durante a semana, a data é automaticamente confirmada
                    st.session_state.devolucao_confirmada = True

            nome_completo = st.session_state.nome_completo
            email_usuario = st.session_state.usuario_logado
            descVeiculo = st.selectbox(label='Carro', key='carro', options=[
                'SWQ1F92 - Versa Advance', 'SVO6A16 - Saveiro', 'TMG0H05 - Volkswagem Virtus', 'FRF6535 - Mercedes Benz Vito VAN'
            ]) 

            descDestino = st.multiselect(label='Cidade', key='destino', options=[
                 "Adamantina", "Adolfo", "Aguaí", "Águas da Prata", "Águas de Lindóia", "Águas de Santa Bárbara", "Águas de São Pedro",
    "Agudos", "Alambari", "Alfredo Marcondes", "Altair", "Altinópolis", "Alto Alegre", "Alumínio", "Álvares Florence",
    "Álvares Machado", "Álvaro de Carvalho", "Alvinlândia", "Americana", "Américo Brasiliense", "Américo de Campos",
    "Amparo", "Analândia", "Andradina", "Angatuba", "Anhembi", "Anhumas", "Aparecida", "Aparecida d'Oeste", "Apiaí",
    "Araçariguama", "Araçatuba", "Araçoiaba da Serra", "Aramina", "Arandu", "Arapeí", "Araraquara", "Araras",
    "Arco-Íris", "Arealva", "Areias", "Areiópolis", "Ariranha", "Artur Nogueira", "Arujá", "Aspásia", "Assis",
    "Atibaia", "Auriflama", "Avaí", "Avanhandava", "Avaré", "Bady Bassitt", "Balbinos", "Bálsamo", "Bananal",
    "Barão de Antonina", "Barbosa", "Bariri", "Barra Bonita", "Barra do Chapéu", "Barra do Turvo", "Barretos", "Barrinha",
    "Barueri", "Bastos", "Batatais", "Bauru", "Bebedouro", "Bento de Abreu", "Bernardino de Campos", "Bertioga",
    "Bilac", "Birigui", "Biritiba-Mirim", "Boa Esperança do Sul", "Bocaina", "Bofete", "Boituva", "Bom Jesus dos Perdões",
    "Bom Sucesso de Itararé", "Borá", "Boracéia", "Borborema", "Borebi", "Botucatu", "Bragança Paulista", "Braúna",
    "Brejo Alegre", "Brodowski", "Brotas", "Buri", "Buritama", "Buritizal", "Cabrália Paulista", "Cabreúva", "Caçapava",
    "Cachoeira Paulista", "Caconde", "Cafelândia", "Caiabu", "Caieiras", "Caiuá", "Cajamar", "Cajati", "Cajobi",
    "Cajuru", "Campina do Monte Alegre", "Campinas", "Campo Limpo Paulista", "Campos do Jordão", "Campos Novos Paulista",
    "Cananéia", "Canas", "Cândido Mota", "Cândido Rodrigues", "Canitar", "Capão Bonito", "Capela do Alto", "Capivari",
    "Caraguatatuba", "Carapicuíba", "Cardoso", "Casa Branca", "Cássia dos Coqueiros", "Castilho", "Catanduva", "Catiguá",
    "Cedral", "Cerqueira César", "Cerquilho", "Cesário Lange", "Charqueada", "Chavantes", "Clementina", "Colina",
    "Colômbia", "Conchal", "Conchas", "Cordeirópolis", "Coroados", "Coronel Macedo", "Corumbataí", "Cosmópolis",
    "Cosmorama", "Cotia", "Cravinhos", "Cristais Paulista", "Cruzália", "Cruzeiro", "Cubatão", "Cunha", "Descalvado",
    "Diadema", "Dirce Reis", "Divinolândia", "Dobrada", "Dois Córregos", "Dolcinópolis", "Dourado", "Dracena", "Duartina",
    "Dumont", "Echaporã", "Eldorado", "Elias Fausto", "Elisiário", "Embaúba", "Embu das Artes", "Embu-Guaçu", "Emilianópolis",
    "Engenheiro Coelho", "Espírito Santo do Pinhal", "Espírito Santo do Turvo", "Estiva Gerbi", "Estrela d'Oeste", "Estrela do Norte",
    "Euclides da Cunha Paulista", "Fartura", "Fernando Prestes", "Fernandópolis", "Fernão", "Ferraz de Vasconcelos",
    "Flora Rica", "Floreal", "Flórida Paulista", "Florínia", "Franca", "Francisco Morato", "Franco da Rocha", "Gabriel Monteiro",
    "Gália", "Garça", "Gastão Vidigal", "Gavião Peixoto", "General Salgado", "Getulina", "Glicério", "Guaiçara", "Guaimbê",
    "Guaíra", "Guapiaçu", "Guapiara", "Guará", "Guaraçaí", "Guaraci", "Guarani d'Oeste", "Guarantã", "Guararapes",
    "Guararema", "Guaratinguetá", "Guareí", "Guariba", "Guarujá", "Guarulhos", "Guatapará", "Guzolândia", "Herculândia",
    "Holambra", "Hortolândia", "Iacanga", "Iacri", "Iaras", "Ibaté", "Ibirá", "Ibirarema", "Ibitinga", "Ibiúna", "Icém",
    "Iepê", "Igaraçu do Tietê", "Igarapava", "Igaratá", "Iguape", "Ilha Comprida", "Ilha Solteira", "Ilhabela", "Indaiatuba",
    "Indiana", "Indiaporã", "Inúbia Paulista", "Ipaussu", "Iperó", "Ipeúna", "Ipiguá", "Iporanga", "Ipuã", "Iracemápolis",
    "Irapuã", "Irapuru", "Itaberá", "Itaí", "Itajobi", "Itaju", "Itanhaém", "Itaóca", "Itapecerica da Serra", "Itapetininga",
    "Itapeva", "Itapevi", "Itapira", "Itapirapuã Paulista", "Itápolis", "Itaporanga", "Itapuí", "Itapura", "Itaquaquecetuba",
    "Itararé", "Itariri", "Itatiba", "Itatinga", "Itirapina", "Itirapuã", "Itobi", "Itu", "Itupeva", "Ituverava", "Jaborandi",
    "Jaboticabal", "Jacareí", "Jaci", "Jacupiranga", "Jaguariúna", "Jales", "Jambeiro", "Jandira", "Jardinópolis", "Jarinu",
    "Jaú", "Jeriquara", "Joanópolis", "João Ramalho", "José Bonifácio", "Júlio Mesquita", "Jumirim", "Jundiaí", "Junqueirópolis",
    "Juquiá", "Juquitiba", "Lagoinha", "Laranjal Paulista", "Lavínia", "Lavrinhas", "Leme", "Lençóis Paulista", "Limeira",
    "Lindóia", "Lins", "Lorena", "Lourdes", "Louveira", "Lucélia", "Lucianópolis", "Luís Antônio", "Luiziânia", "Lupércio",
    "Lutécia", "Macatuba", "Macaubal", "Macedônia", "Magda", "Mairinque", "Mairiporã", "Manduri", "Marabá Paulista",
    "Maracaí", "Marapoama", "Mariápolis", "Marília", "Marinópolis", "Martinópolis", "Matão", "Mauá", "Mendonça",
    "Meridiano", "Mesópolis", "Miguelópolis", "Mineiros do Tietê", "Mira Estrela", "Miracatu", "Mirandópolis", "Mirante do Paranapanema",
    "Mirassol", "Mirassolândia", "Mococa", "Mogi das Cruzes", "Mogi Guaçu", "Moji Mirim", "Mombuca", "Monções", "Mongaguá",
    "Monte Alegre do Sul", "Monte Alto", "Monte Aprazível", "Monte Azul Paulista", "Monte Castelo", "Monte Mor", "Monteiro Lobato",
    "Morro Agudo", "Morungaba", "Motuca", "Murutinga do Sul", "Nantes", "Narandiba", "Natividade da Serra", "Nazaré Paulista",
    "Neves Paulista", "Nhandeara", "Nipoã", "Nova Aliança", "Nova Campina", "Nova Canaã Paulista", "Nova Castilho",
    "Nova Europa", "Nova Granada", "Nova Guataporanga", "Nova Independência", "Nova Luzitânia", "Nova Odessa", "Novais",
    "Novo Horizonte", "Nuporanga", "Ocauçu", "Óleo", "Olímpia", "Onda Verde", "Oriente", "Orindiúva", "Orlândia", "Osasco",
    "Oscar Bressane", "Osvaldo Cruz", "Ourinhos", "Ouro Verde", "Ouroeste", "Pacaembu", "Palestina", "Palmares Paulista",
    "Palmeira d'Oeste", "Palmital", "Panorama", "Paraguaçu Paulista", "Paraibuna", "Paraíso", "Paranapanema", "Paranapuã",
    "Parapuã", "Pardinho", "Pariquera-Açu", "Parisi", "Patrocínio Paulista", "Paulicéia", "Paulínia", "Paulistânia", "Paulo de Faria",
    "Pederneiras", "Pedra Bela", "Pedranópolis", "Pedregulho", "Pedreira", "Pedrinhas Paulista", "Pedro de Toledo", "Penápolis",
    "Pereira Barreto", "Pereiras", "Peruíbe", "Piacatu", "Piedade", "Pilar do Sul", "Pindamonhangaba", "Pindorama", "Pinhalzinho",
    "Piquerobi", "Piquete", "Piracaia", "Piracicaba", "Piraju", "Pirajuí", "Pirangi", "Pirapora do Bom Jesus", "Pirapozinho",
    "Pirassununga", "Piratininga", "Pitangueiras", "Planalto", "Platina", "Poá", "Poloni", "Pompéia", "Pongaí", "Pontal",
    "Pontalinda", "Pontes Gestal", "Populina", "Porangaba", "Porto Feliz", "Porto Ferreira", "Potim", "Potirendaba", "Pracinha",
    "Pradópolis", "Praia Grande", "Pratânia", "Presidente Alves", "Presidente Bernardes", "Presidente Epitácio", "Presidente Prudente",
    "Presidente Venceslau", "Promissão", "Quadra", "Quatá", "Queiroz", "Queluz", "Quintana", "Rafard", "Rancharia", "Redenção da Serra",
    "Regente Feijó", "Reginópolis", "Registro", "Restinga", "Ribeira", "Ribeirão Bonito", "Ribeirão Branco", "Ribeirão Corrente",
    "Ribeirão do Sul", "Ribeirão dos Índios", "Ribeirão Grande", "Ribeirão Pires", "Ribeirão Preto", "Rifaina", "Rincão", "Rinópolis",
    "Rio Claro", "Rio das Pedras", "Rio Grande da Serra", "Riolândia", "Riversul", "Rosana", "Roseira", "Rubiácea", "Rubinéia",
    "Sabino", "Sagres", "Sales", "Sales Oliveira", "Salesópolis", "Salmourão", "Saltinho", "Salto", "Salto de Pirapora",
    "Salto Grande", "Sandovalina", "Santa Adélia", "Santa Albertina", "Santa Bárbara d'Oeste", "Santa Branca", "Santa Clara d'Oeste",
    "Santa Cruz da Conceição", "Santa Cruz da Esperança", "Santa Cruz das Palmeiras", "Santa Cruz do Rio Pardo", "Santa Ernestina",
    "Santa Fé do Sul", "Santa Gertrudes", "Santa Isabel", "Santa Lúcia", "Santa Maria da Serra", "Santa Mercedes", "Santa Rita d'Oeste",
    "Santa Rita do Passa Quatro", "Santa Rosa de Viterbo", "Santa Salete", "Santana da Ponte Pensa", "Santana de Parnaíba",
    "Santo Anastácio", "Santo André", "Santo Antônio da Alegria", "Santo Antônio de Posse", "Santo Antônio do Aracanguá", "Santo Antônio do Jardim",
    "Santo Antônio do Pinhal", "Santo Expedito", "Santópolis do Aguapeí", "Santos", "São Bento do Sapucaí", "São Bernardo do Campo",
    "São Caetano do Sul", "São Carlos", "São Francisco", "São João da Boa Vista", "São João das Duas Pontes", "São João de Iracema",
    "São João do Pau d'Alho", "São Joaquim da Barra", "São José da Bela Vista", "São José do Barreiro", "São José do Rio Pardo",
    "São José do Rio Preto", "São José dos Campos", "São Lourenço da Serra", "São Luiz do Paraitinga", "São Manuel", "São Miguel Arcanjo",
    "São Paulo", "São Pedro", "São Pedro do Turvo", "São Roque", "São Sebastião", "São Sebastião da Grama", "São Simão", "São Vicente",
    "Sarapuí", "Sarutaiá", "Sebastianópolis do Sul", "Serra Azul", "Serra Negra", "Serrana", "Sertãozinho", "Sete Barras",
    "Severínia", "Silveiras", "Socorro", "Sorocaba", "Sud Mennucci", "Sumaré", "Suzanápolis", "Suzano", "Tabapuã", "Tabatinga",
    "Taboão da Serra", "Taciba", "Taguaí", "Taiaçu", "Taiúva", "Tambaú", "Tanabi", "Tapiraí", "Tapiratiba", "Taquaral", "Taquaritinga",
    "Taquarituba", "Taquarivaí", "Tarabai", "Tarumã", "Tatuí", "Taubaté", "Tejupá", "Teodoro Sampaio", "Terra Roxa", "Tietê",
    "Timburi", "Torre de Pedra", "Torrinha", "Trabiju", "Tremembé", "Três Fronteiras", "Tuiuti", "Tupã", "Tupi Paulista",
    "Turiúba", "Turmalina", "Ubarana", "Ubatuba", "Ubirajara", "Uchoa", "União Paulista", "Urânia", "Uru", "Urupês", "Valentim Gentil",
    "Valinhos", "Valparaíso", "Vargem", "Vargem Grande do Sul", "Vargem Grande Paulista", "Várzea Paulista", "Vera Cruz", "Vinhedo",
    "Viradouro", "Vista Alegre do Alto", "Vitória Brasil", "Votorantim", "Votuporanga", "Zacarias"
            ])

            hoje = datetime.now().date()

            # Se tudo for confirmado, pode cadastrar a reserva
            if not (dtRetirada and hrRetirada and dtDevolucao and hrDevolucao and descVeiculo and descDestino):
                btnCadastrar = st.button('Cadastrar', key='botao_cadastrar', disabled=True)
            else:
                btnCadastrar = st.button('Cadastrar', key='botao_cadastrar', disabled=False)
                if btnCadastrar:
                    # Verificar se as datas foram confirmadas, ou se não são finais de semana
                    if (dtRetirada.weekday() >= 5 and not st.session_state.retirada_confirmada) or (dtDevolucao.weekday() >= 5 and not st.session_state.devolucao_confirmada):
                        st.error('Por favor, confirme as datas selecionadas.')
                    elif dtRetirada < hoje or dtDevolucao < hoje:
                        st.error('Não é possível fazer uma reserva para uma data passada.')
                    elif dtDevolucao < dtRetirada:
                        st.error('A data de devolução não pode ser anterior à data de retirada.')
                    else:
                        adicionar_reserva(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, descVeiculo, descDestino)
                        
                        # Resetar confirmações
                        st.session_state.retirada_confirmada = False
                        st.session_state.devolucao_confirmada = False

        with st.form(key='buscar_reserva'):
            st.subheader('Consultar Reservas')
            col1, col2 = st.columns(2)

            with col1:
                dtRetirada_filtro = st.date_input(label='Data de Retirada', key='dtRetirada_filtro', value=None, format='DD/MM/YYYY')

            with col2:
                dtDevolucao_filtro = st.date_input(label='Data de Devolução', key='dtDevolucao_filtro', value=None, format='DD/MM/YYYY')

            col3, col4 = st.columns(2)

            with col3:
                carro_filtro = st.multiselect(label='Carro', key='carro_filtro', options=['SWQ1F92 - Versa Advance', 'SVO6A16 - Saveiro', 'TMG0H05 - Volkswagem Virtus', 'FRF6535 - Mercedes Benz Vito VAN'
            ])

            with col4:
                cidade_filtro = st.multiselect(label='Cidade', key='cidade_filtro', options=[ "Adamantina", "Adolfo", "Aguaí", "Águas da Prata", "Águas de Lindóia", "Águas de Santa Bárbara", "Águas de São Pedro",
    "Agudos", "Alambari", "Alfredo Marcondes", "Altair", "Altinópolis", "Alto Alegre", "Alumínio", "Álvares Florence",
    "Álvares Machado", "Álvaro de Carvalho", "Alvinlândia", "Americana", "Américo Brasiliense", "Américo de Campos",
    "Amparo", "Analândia", "Andradina", "Angatuba", "Anhembi", "Anhumas", "Aparecida", "Aparecida d'Oeste", "Apiaí",
    "Araçariguama", "Araçatuba", "Araçoiaba da Serra", "Aramina", "Arandu", "Arapeí", "Araraquara", "Araras",
    "Arco-Íris", "Arealva", "Areias", "Areiópolis", "Ariranha", "Artur Nogueira", "Arujá", "Aspásia", "Assis",
    "Atibaia", "Auriflama", "Avaí", "Avanhandava", "Avaré", "Bady Bassitt", "Balbinos", "Bálsamo", "Bananal",
    "Barão de Antonina", "Barbosa", "Bariri", "Barra Bonita", "Barra do Chapéu", "Barra do Turvo", "Barretos", "Barrinha",
    "Barueri", "Bastos", "Batatais", "Bauru", "Bebedouro", "Bento de Abreu", "Bernardino de Campos", "Bertioga",
    "Bilac", "Birigui", "Biritiba-Mirim", "Boa Esperança do Sul", "Bocaina", "Bofete", "Boituva", "Bom Jesus dos Perdões",
    "Bom Sucesso de Itararé", "Borá", "Boracéia", "Borborema", "Borebi", "Botucatu", "Bragança Paulista", "Braúna",
    "Brejo Alegre", "Brodowski", "Brotas", "Buri", "Buritama", "Buritizal", "Cabrália Paulista", "Cabreúva", "Caçapava",
    "Cachoeira Paulista", "Caconde", "Cafelândia", "Caiabu", "Caieiras", "Caiuá", "Cajamar", "Cajati", "Cajobi",
    "Cajuru", "Campina do Monte Alegre", "Campinas", "Campo Limpo Paulista", "Campos do Jordão", "Campos Novos Paulista",
    "Cananéia", "Canas", "Cândido Mota", "Cândido Rodrigues", "Canitar", "Capão Bonito", "Capela do Alto", "Capivari",
    "Caraguatatuba", "Carapicuíba", "Cardoso", "Casa Branca", "Cássia dos Coqueiros", "Castilho", "Catanduva", "Catiguá",
    "Cedral", "Cerqueira César", "Cerquilho", "Cesário Lange", "Charqueada", "Chavantes", "Clementina", "Colina",
    "Colômbia", "Conchal", "Conchas", "Cordeirópolis", "Coroados", "Coronel Macedo", "Corumbataí", "Cosmópolis",
    "Cosmorama", "Cotia", "Cravinhos", "Cristais Paulista", "Cruzália", "Cruzeiro", "Cubatão", "Cunha", "Descalvado",
    "Diadema", "Dirce Reis", "Divinolândia", "Dobrada", "Dois Córregos", "Dolcinópolis", "Dourado", "Dracena", "Duartina",
    "Dumont", "Echaporã", "Eldorado", "Elias Fausto", "Elisiário", "Embaúba", "Embu das Artes", "Embu-Guaçu", "Emilianópolis",
    "Engenheiro Coelho", "Espírito Santo do Pinhal", "Espírito Santo do Turvo", "Estiva Gerbi", "Estrela d'Oeste", "Estrela do Norte",
    "Euclides da Cunha Paulista", "Fartura", "Fernando Prestes", "Fernandópolis", "Fernão", "Ferraz de Vasconcelos",
    "Flora Rica", "Floreal", "Flórida Paulista", "Florínia", "Franca", "Francisco Morato", "Franco da Rocha", "Gabriel Monteiro",
    "Gália", "Garça", "Gastão Vidigal", "Gavião Peixoto", "General Salgado", "Getulina", "Glicério", "Guaiçara", "Guaimbê",
    "Guaíra", "Guapiaçu", "Guapiara", "Guará", "Guaraçaí", "Guaraci", "Guarani d'Oeste", "Guarantã", "Guararapes",
    "Guararema", "Guaratinguetá", "Guareí", "Guariba", "Guarujá", "Guarulhos", "Guatapará", "Guzolândia", "Herculândia",
    "Holambra", "Hortolândia", "Iacanga", "Iacri", "Iaras", "Ibaté", "Ibirá", "Ibirarema", "Ibitinga", "Ibiúna", "Icém",
    "Iepê", "Igaraçu do Tietê", "Igarapava", "Igaratá", "Iguape", "Ilha Comprida", "Ilha Solteira", "Ilhabela", "Indaiatuba",
    "Indiana", "Indiaporã", "Inúbia Paulista", "Ipaussu", "Iperó", "Ipeúna", "Ipiguá", "Iporanga", "Ipuã", "Iracemápolis",
    "Irapuã", "Irapuru", "Itaberá", "Itaí", "Itajobi", "Itaju", "Itanhaém", "Itaóca", "Itapecerica da Serra", "Itapetininga",
    "Itapeva", "Itapevi", "Itapira", "Itapirapuã Paulista", "Itápolis", "Itaporanga", "Itapuí", "Itapura", "Itaquaquecetuba",
    "Itararé", "Itariri", "Itatiba", "Itatinga", "Itirapina", "Itirapuã", "Itobi", "Itu", "Itupeva", "Ituverava", "Jaborandi",
    "Jaboticabal", "Jacareí", "Jaci", "Jacupiranga", "Jaguariúna", "Jales", "Jambeiro", "Jandira", "Jardinópolis", "Jarinu",
    "Jaú", "Jeriquara", "Joanópolis", "João Ramalho", "José Bonifácio", "Júlio Mesquita", "Jumirim", "Jundiaí", "Junqueirópolis",
    "Juquiá", "Juquitiba", "Lagoinha", "Laranjal Paulista", "Lavínia", "Lavrinhas", "Leme", "Lençóis Paulista", "Limeira",
    "Lindóia", "Lins", "Lorena", "Lourdes", "Louveira", "Lucélia", "Lucianópolis", "Luís Antônio", "Luiziânia", "Lupércio",
    "Lutécia", "Macatuba", "Macaubal", "Macedônia", "Magda", "Mairinque", "Mairiporã", "Manduri", "Marabá Paulista",
    "Maracaí", "Marapoama", "Mariápolis", "Marília", "Marinópolis", "Martinópolis", "Matão", "Mauá", "Mendonça",
    "Meridiano", "Mesópolis", "Miguelópolis", "Mineiros do Tietê", "Mira Estrela", "Miracatu", "Mirandópolis", "Mirante do Paranapanema",
    "Mirassol", "Mirassolândia", "Mococa", "Mogi das Cruzes", "Mogi Guaçu", "Moji Mirim", "Mombuca", "Monções", "Mongaguá",
    "Monte Alegre do Sul", "Monte Alto", "Monte Aprazível", "Monte Azul Paulista", "Monte Castelo", "Monte Mor", "Monteiro Lobato",
    "Morro Agudo", "Morungaba", "Motuca", "Murutinga do Sul", "Nantes", "Narandiba", "Natividade da Serra", "Nazaré Paulista",
    "Neves Paulista", "Nhandeara", "Nipoã", "Nova Aliança", "Nova Campina", "Nova Canaã Paulista", "Nova Castilho",
    "Nova Europa", "Nova Granada", "Nova Guataporanga", "Nova Independência", "Nova Luzitânia", "Nova Odessa", "Novais",
    "Novo Horizonte", "Nuporanga", "Ocauçu", "Óleo", "Olímpia", "Onda Verde", "Oriente", "Orindiúva", "Orlândia", "Osasco",
    "Oscar Bressane", "Osvaldo Cruz", "Ourinhos", "Ouro Verde", "Ouroeste", "Pacaembu", "Palestina", "Palmares Paulista",
    "Palmeira d'Oeste", "Palmital", "Panorama", "Paraguaçu Paulista", "Paraibuna", "Paraíso", "Paranapanema", "Paranapuã",
    "Parapuã", "Pardinho", "Pariquera-Açu", "Parisi", "Patrocínio Paulista", "Paulicéia", "Paulínia", "Paulistânia", "Paulo de Faria",
    "Pederneiras", "Pedra Bela", "Pedranópolis", "Pedregulho", "Pedreira", "Pedrinhas Paulista", "Pedro de Toledo", "Penápolis",
    "Pereira Barreto", "Pereiras", "Peruíbe", "Piacatu", "Piedade", "Pilar do Sul", "Pindamonhangaba", "Pindorama", "Pinhalzinho",
    "Piquerobi", "Piquete", "Piracaia", "Piracicaba", "Piraju", "Pirajuí", "Pirangi", "Pirapora do Bom Jesus", "Pirapozinho",
    "Pirassununga", "Piratininga", "Pitangueiras", "Planalto", "Platina", "Poá", "Poloni", "Pompéia", "Pongaí", "Pontal",
    "Pontalinda", "Pontes Gestal", "Populina", "Porangaba", "Porto Feliz", "Porto Ferreira", "Potim", "Potirendaba", "Pracinha",
    "Pradópolis", "Praia Grande", "Pratânia", "Presidente Alves", "Presidente Bernardes", "Presidente Epitácio", "Presidente Prudente",
    "Presidente Venceslau", "Promissão", "Quadra", "Quatá", "Queiroz", "Queluz", "Quintana", "Rafard", "Rancharia", "Redenção da Serra",
    "Regente Feijó", "Reginópolis", "Registro", "Restinga", "Ribeira", "Ribeirão Bonito", "Ribeirão Branco", "Ribeirão Corrente",
    "Ribeirão do Sul", "Ribeirão dos Índios", "Ribeirão Grande", "Ribeirão Pires", "Ribeirão Preto", "Rifaina", "Rincão", "Rinópolis",
    "Rio Claro", "Rio das Pedras", "Rio Grande da Serra", "Riolândia", "Riversul", "Rosana", "Roseira", "Rubiácea", "Rubinéia",
    "Sabino", "Sagres", "Sales", "Sales Oliveira", "Salesópolis", "Salmourão", "Saltinho", "Salto", "Salto de Pirapora",
    "Salto Grande", "Sandovalina", "Santa Adélia", "Santa Albertina", "Santa Bárbara d'Oeste", "Santa Branca", "Santa Clara d'Oeste",
    "Santa Cruz da Conceição", "Santa Cruz da Esperança", "Santa Cruz das Palmeiras", "Santa Cruz do Rio Pardo", "Santa Ernestina",
    "Santa Fé do Sul", "Santa Gertrudes", "Santa Isabel", "Santa Lúcia", "Santa Maria da Serra", "Santa Mercedes", "Santa Rita d'Oeste",
    "Santa Rita do Passa Quatro", "Santa Rosa de Viterbo", "Santa Salete", "Santana da Ponte Pensa", "Santana de Parnaíba",
    "Santo Anastácio", "Santo André", "Santo Antônio da Alegria", "Santo Antônio de Posse", "Santo Antônio do Aracanguá", "Santo Antônio do Jardim",
    "Santo Antônio do Pinhal", "Santo Expedito", "Santópolis do Aguapeí", "Santos", "São Bento do Sapucaí", "São Bernardo do Campo",
    "São Caetano do Sul", "São Carlos", "São Francisco", "São João da Boa Vista", "São João das Duas Pontes", "São João de Iracema",
    "São João do Pau d'Alho", "São Joaquim da Barra", "São José da Bela Vista", "São José do Barreiro", "São José do Rio Pardo",
    "São José do Rio Preto", "São José dos Campos", "São Lourenço da Serra", "São Luiz do Paraitinga", "São Manuel", "São Miguel Arcanjo",
    "São Paulo", "São Pedro", "São Pedro do Turvo", "São Roque", "São Sebastião", "São Sebastião da Grama", "São Simão", "São Vicente",
    "Sarapuí", "Sarutaiá", "Sebastianópolis do Sul", "Serra Azul", "Serra Negra", "Serrana", "Sertãozinho", "Sete Barras",
    "Severínia", "Silveiras", "Socorro", "Sorocaba", "Sud Mennucci", "Sumaré", "Suzanápolis", "Suzano", "Tabapuã", "Tabatinga",
    "Taboão da Serra", "Taciba", "Taguaí", "Taiaçu", "Taiúva", "Tambaú", "Tanabi", "Tapiraí", "Tapiratiba", "Taquaral", "Taquaritinga",
    "Taquarituba", "Taquarivaí", "Tarabai", "Tarumã", "Tatuí", "Taubaté", "Tejupá", "Teodoro Sampaio", "Terra Roxa", "Tietê",
    "Timburi", "Torre de Pedra", "Torrinha", "Trabiju", "Tremembé", "Três Fronteiras", "Tuiuti", "Tupã", "Tupi Paulista",
    "Turiúba", "Turmalina", "Ubarana", "Ubatuba", "Ubirajara", "Uchoa", "União Paulista", "Urânia", "Uru", "Urupês", "Valentim Gentil",
    "Valinhos", "Valparaíso", "Vargem", "Vargem Grande do Sul", "Vargem Grande Paulista", "Várzea Paulista", "Vera Cruz", "Vinhedo",
    "Viradouro", "Vista Alegre do Alto", "Vitória Brasil", "Votorantim", "Votuporanga", "Zacarias"])

            buscar_reserva = st.form_submit_button(label='Buscar Reserva')

        if buscar_reserva:
            df_reservas = buscar_reservas_filtros(dtRetirada_filtro, dtDevolucao_filtro, carro_filtro, cidade_filtro)
            if df_reservas.empty:
                st.error('Nenhuma reserva encontrada.')
            else:
                df_selecao = criar_df_para_visualizacao(df_reservas)
                st.dataframe(df_selecao)
                st.session_state.df_selecao = df_selecao
                if st.button('Recarregar Dados', key='recarregar_dados_consulta'):
                    limpar_cache()

        st.title('Todas as Reservas')
        exibir_reservas_interativas()

    else:
        menu_autenticacao = st.sidebar.radio('Selecione uma opção', ['Login', 'Cadastro', 'Recuperar Senha'])

        if menu_autenticacao == 'Login':
            login()
        elif menu_autenticacao == 'Cadastro':
            cadastro()
        elif menu_autenticacao == 'Recuperar Senha':
            email = st.text_input("Digite seu email:")
            if st.button("Recuperar Senha"):
                if email:
                    recuperar_senha(email)
                    st.success("Um email com link de recuperação foi enviado!")


# Exibe a página inicial ou outras páginas
params = st.experimental_get_query_params()
token = params.get('token', [None])[0]  # <- Captura correta do token

if token:
    resetar_senha()
else:
    if st.session_state.get('pagina') == 'home':
        home_page()
    elif st.session_state.get('pagina') == 'reservas':
        st.title('Todas as Reservas')
        exibir_reservas_interativas()
        if st.button('Voltar'):
            st.session_state.pagina = 'home'
            st.query_params(pagina='home')  # <- Este pode ser removido, pois `st.query_params` não existe
    else:
        home_page()