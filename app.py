from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import locale

# INICIALIZAÇÃO DA APLICAÇÃO
app = Flask(__name__)

# CHAVE DE SEGURANÇA DA APLICAÇÃO
app.secret_key = 'B9783E9009E7B43C5A4FC70851D7023B5AF1D802290528034EE46EE1C26A4524'

# CONEXÃO COM O BANCO DE DADOS
app.config['SQLALCHEMY_DATABASE_URI'] = '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
    SGBD = 'mysql+mysqlconnector',
    usuario = 'frederico',
    senha = 'Dequi.5812',
    servidor = 'localhost',
    database = 'teste_carteira'
)
db = SQLAlchemy(app)

class Carteira1(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    nome = db.Column(db.String(90), nullable=False)
    dia = db.Column(db.Date, nullable=False)
    valor = db. Column(db.Float(14))

class Carteira2(db.Model):
    __tablename__ = 'carteira2'

    iditem = db.Column(db.Integer(), primary_key=True)
    usuario_idusuario = db.Column(db.Integer(), ForeignKey('usuario1.idusuario'))
    usuario = relationship('Usuario1')
    tipo = db.Column(db.String(255), nullable=False)
    dia = db.Column(db.Date, nullable=False)
    valor = db. Column(db.Float(14))

class Usuario1(db.Model):
    __tablename__ = 'usuario1'

    idusuario = db.Column(db.Integer(), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    login = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    cadastro = db.Column(db.DateTime, nullable=False)

# Configuração do Locale para reconhecer o REAL
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# ROTA PRINCIPAL
@app.route('/', methods=['GET', 'POST'])
def index():
    
    nome_pagina = "Logar Usuário"
    return render_template('app.html', nome_pagina=nome_pagina)

@app.route('/auth', methods=['GET', 'POST'])
def autenticar():
    usuario = Usuario1.query.filter_by(login=request.form['login'], senha=request.form['senha']).first()

    if usuario:
        if request.form['login'] == usuario.login:
            if request.form['senha'] == usuario.senha:
                session['usuario_logado'] = usuario.idusuario
                flash(usuario.nome + 'logado com sucesso!')
                return redirect(url_for('home'))
    else:
        flash('Usuário ou senha incorreto!')
        return redirect('/index')

@app.route('/new_user', methods=['GET', 'POST'])
def novo_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        cpf = request.form.get('cpf')
        email = request.form.get('email')
        login = request.form.get('login')
        senha = request.form.get('login')
        novo_valor = Usuario1(nome=nome, sobrenome=sobrenome, cpf=cpf, email=email, login=login, senha=senha)
        db.session.add(novo_valor)
        db.session.commit()
        return redirect(url_for('home'))
    
    nome_pagina = "Criar Usuário"
    return render_template('new_user.html', nome_pagina=nome_pagina)

@app.route('/home')
def home():
    dados_carteira = Carteira2.query.order_by(Carteira2.usuario_idusuario == session['usuario_logado'].idusuario).all()

    # Calculando a soma dos valores
    total_valores = db.session.query(func.sum(Carteira2.valor)).scalar() or 0.0
    total_valores = locale.currency(total_valores, grouping=True)

    # Formatando os valores para REAL e DATA para o padrão Brasileiro
    for item in dados_carteira:
        item.valor = locale.currency(item.valor, grouping=True)
        data_formatada = f"{str(item.dia.day).zfill(2)}/{str(item.dia.month).zfill(2)}/{item.dia.year}"
        item.data_formatada = data_formatada

    nome_pagina = "Extrato"
    return render_template('home.html', carteira=dados_carteira, total_valores=total_valores, nome_pagina=nome_pagina)

# ADICIONAR NOVAS INFORMAÇÕES
@app.route('/novo', methods=['GET', 'POST'])
def novo_item():
    if request.method == 'POST':
        nome = request.form.get('nome')
        dia = request.form.get('dia')
        valor = request.form.get('valor')
        novo_valor = Carteira1(nome=nome, dia=dia, valor=valor)
        db.session.add(novo_valor)
        db.session.commit()
        return redirect(url_for('home'))
    
    nome_pagina = "Adicionar Transação"
    return render_template('novo.html', nome_pagina=nome_pagina)

# EDITAR INFORMAÇÕES SALVAS
@app.route('/edit/<int:id>', methods=["GET", 'POST'])
def editar_item(id):
    item_para_editar = Carteira1.query.get(id)
    if request.method == 'POST':
        item_para_editar.nome = request.form.get('nome')
        item_para_editar.dia = request.form.get('dia')
        item_para_editar.valor = request.form.get('valor')
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('editar.html', item=item_para_editar)

# APAGAR INFORMAÇÕES SALVAS
@app.route('/excluir/<int:id>', methods=['POST', ])
def excluir_item(id):
    item_remover = Carteira1.query.get(id)
    if item_remover:
        db.session.delete(item_remover)
        db.session.commit()
    return redirect(url_for('home'))

# START DA APLICAÇÃO
if __name__ == '__main__':
    app.run(debug=True)