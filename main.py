import streamlit as st
import pandas as pd
from datetime import datetime, time
import sqlite3
import hashlib
import smtplib
import os
import base64
from email.mime.text import MIMEText
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from email.mime.multipart import MIMEMultipart
import random
import string
import uuid
import warnings
from datetime import datetime

# Configurações iniciais
st.set_page_config(layout='wide', page_title="Frota Vilaurbe", page_icon=":car:")

# Suprime os avisos do Streamlit
warnings.filterwarnings("ignore", message="Please replace st.experimental_get_query_params with st.query_params.")

# Função para gerar um token aleatório
def gerar_token_tamanho_aleatorio(tamanho=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))

# Função para conectar ao banco de dados SQLite
def conectar_banco():
    return sqlite3.connect('reservas.db')

# Função para salvar token no banco de dados
def salvar_token_no_banco(email, token):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tokens (email, token) VALUES (?, ?)', (email, token))
    conn.commit()
    conn.close()

# Função para enviar email de recuperação de senha
def enviar_email_recovery(destinatario, link):
    servidor_smtp = 'smtp.office365.com'
    porta = 587
    remetente = 'ti@vilaurbe.com.br'
    senha = 'Vilaurbe2024!'

    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = 'Frota Vilaurbe - Recuperação de Senha'

        corpo_email = f'Acesse o link para redefinir sua senha: {link}'
        msg.attach(MIMEText(corpo_email, 'plain'))

        with smtplib.SMTP(servidor_smtp, porta) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())

        st.success("Email enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")

# Função para redefinir senha
def resetar_senha():
    st.title('Redefinir Senha')
    token = st.experimental_get_query_params().get('token', [None])[0]

    if not token:
        st.error("Token inválido ou expirado.")
        return

    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM tokens WHERE token = ?', (token,))
    result = cursor.fetchone()
    conn.close()

    if result:
        email = result[0]
        st.text_input("E-mail", value=email, disabled=True)
        nova_senha = st.text_input("Nova Senha", type="password")
        confirmar_senha = st.text_input("Confirmar Senha", type="password")

        if st.button("Redefinir Senha"):
            if nova_senha != confirmar_senha:
                st.error("As senhas não correspondem.")
            else:
                atualizar_senha_com_token(token, nova_senha)
    else:
        st.error("Token inválido ou expirado.")

# Função para atualizar a senha com token
def atualizar_senha_com_token(token, nova_senha):
    senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('UPDATE usuarios SET senha = ? WHERE email = (SELECT email FROM tokens WHERE token = ?)', (senha_hash, token))
    cursor.execute('DELETE FROM tokens WHERE token = ?', (token,))
    conn.commit()
    conn.close()

# Função de login
def login():
    st.subheader('Login')
    email = st.text_input('E-mail')
    senha = st.text_input('Senha', type='password')
    
    if st.button('Entrar'):
        if verificar_usuario(email, senha):
            st.session_state.usuario_logado = email
            st.session_state.pagina = 'reservas'
            st.success("Login realizado com sucesso!")
            st.experimental_rerun()
        else:
            st.error("E-mail ou senha incorretos.")

# Função para verificar se o usuário existe
def verificar_usuario(email, senha):
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha_hash))
    result = cursor.fetchone()
    conn.close()
    return bool(result)

# Função de cadastro
def cadastro():
    st.subheader('Cadastro')
    nome = st.text_input('Nome Completo')
    email = st.text_input('E-mail')
    senha = st.text_input('Senha', type='password')
    confirmar_senha = st.text_input('Confirmar Senha', type='password')

    if st.button('Cadastrar'):
        if senha == confirmar_senha:
            adicionar_usuario(nome, email, senha)
        else:
            st.error("As senhas não correspondem.")

# Função para adicionar usuário
def adicionar_usuario(nome, email, senha):
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuarios (nome_completo, email, senha) VALUES (?, ?, ?)', (nome, email, senha_hash))
        conn.commit()
        st.success("Usuário cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        st.error("Usuário já cadastrado.")
    finally:
        conn.close()

# Função para logout
def logout():
    st.session_state.usuario_logado = None
    st.session_state.pagina = 'login'
    st.success("Você saiu com sucesso.")
    st.experimental_rerun()

# Página inicial
def home_page():
    if 'usuario_logado' in st.session_state and st.session_state.usuario_logado:
        st.sidebar.header(f"Bem-vindo, {st.session_state.usuario_logado}")
        if st.sidebar.button("Logout"):
            logout()

        st.title("Reservas")
        # Aqui você pode adicionar a função de exibir reservas, cadastro de novas reservas, etc.
        exibir_reservas_interativas()
    else:
        login()

# Função para exibir reservas interativas
def exibir_reservas_interativas():
    st.subheader('Visualizar Reservas')
    df_reservas = carregar_reservas_do_banco()
    if not df_reservas.empty:
        AgGrid(df_reservas)
    else:
        st.warning("Nenhuma reserva encontrada.")

# Função para carregar reservas do banco de dados
def carregar_reservas_do_banco():
    conn = conectar_banco()
    query = "SELECT * FROM reservas"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Função principal
def main():
    st.sidebar.title("Sistema de Reservas")

    # Verifica o estado da página e navega entre elas
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'home'

    if st.session_state.pagina == 'home':
        home_page()
    elif st.session_state.pagina == 'login':
        login()
    elif st.session_state.pagina == 'cadastro':
        cadastro()
    elif st.session_state.pagina == 'reservas':
        home_page()

if __name__ == "__main__":
    main()
