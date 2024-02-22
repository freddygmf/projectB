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

class Cc1(db.Model):
    __tablename__ = 'cc1'

    idcc = db.Column(db.Integer(), primary_key=True)
    usuario_idusuario = db.Column(db.Integer(), ForeignKey('usuario1.idusuario'))
    usuario = relationship('Usuario1')
    banco = db.Column(db.String(100), nullable=False)
    bandeira = db.Column(db.String(100), nullable=False)
    lastd = db.Column(db.String(100), nullable=False)
    limite = db.Column(db.Float(14))
    validade = db.Column(db.Date, nullable=False)

# Configuração do Locale para reconhecer o REAL
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# ROTA PRINCIPAL
@app.route('/', methods=['GET', 'POST'])
def index():
    nome_pagina = "Página Inicial"
    return render_template('app.html', nome_pagina=nome_pagina)

# ROTAS PARA INICIAR / FINALIZAR UMA SESSION
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    nome_pagina = "Logar Usuário"
    return render_template('login.html', nome_pagina=nome_pagina)


@app.route('/auth', methods=['GET', 'POST'])
def autenticar():
    usuario = Usuario1.query.filter_by(login=request.form['login'], senha=request.form['senha']).first()

    if usuario:
        if request.form['login'] == usuario.login:
            if request.form['senha'] == usuario.senha:
                session['usuario_logado'] = usuario.idusuario
                flash(usuario.nome + ' ' + usuario.sobrenome + ' logado com sucesso!')
                return redirect(url_for('home'))
    else:
        flash('Usuário ou senha incorreto!')
        return redirect(url_for('login'))
    
@app.route('/dauth')
def deslogar():
    session.pop('usuario_logado', None)
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('index'))

# ROTA PARA REGISTRAR UM NOVO USUÁRIO NA APLICAÇÃO
@app.route('/new_user', methods=['GET', 'POST'])
def novo_usuario():
    if 'usuario_logado' in session:
        return redirect(url_for('home'))
    else:    
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

# Pagina home onde comtém as informações gerais da aplicação
@app.route('/home')
def home():
    if 'usuario_logado' not in session or ['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:
        # Filtra na tabela onde tem os dados do usuário logado
        idusuario = session.get('usuario_logado')
        usuario = Usuario1.query.get(idusuario)
        dados_carteira = Carteira2.query.filter_by(usuario=usuario).all()
        verificador_de_tabela = Carteira2.query.filter_by(usuario=usuario).first()

        if verificador_de_tabela is not None:
            
            # Calculando a soma dos valores
            total_valores = db.session.query(func.sum(Carteira2.valor)).scalar() or 0.0
            total_valores = locale.currency(total_valores, grouping=True)

            # Formatando os valores da MOEDA e DATA para o padrão Brasileiro
            for item in dados_carteira:
                item.valor = locale.currency(item.valor, grouping=True)
                data_formatada = f"{str(item.dia.day).zfill(2)}/{str(item.dia.month).zfill(2)}/{item.dia.year}"
                item.data_formatada = data_formatada

            nome_pagina = "Extrato"
            return render_template('home.html', carteira=dados_carteira, total_valores=total_valores, nome_pagina=nome_pagina)

        else:
            return redirect(url_for('novo_item'))

@app.route('/cc')
def cc():
    if 'usuario_logado' not in session or ['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:
        # Filtra na tabela onde tem os dados do usuário logado
        idusuario = session.get('usuario_logado')
        usuario = Usuario1.query.get(idusuario)
        dados_cc = Cc1.query.filter_by(usuario=usuario).all()
        verificador_de_tabela = Cc1.query.filter_by(usuario=usuario).first()
        
        if verificador_de_tabela is not None:
            
            # SOMANDO TODOS OS VALORES DE LIMITE
            total_limite = db.session.query(func.sum(Cc1.limite)).scalar() or 0.0
            total_limite = locale.currency(total_limite, grouping=True)

        nome_pagina = "Extrato"
        return render_template('cc.html', nome_pagina=nome_pagina, dados_cc=dados_cc, total_limite=total_limite, usuario=usuario.nome + " " + usuario.sobrenome)

# ADICIONAR NOVAS INFORMAÇÕES
@app.route('/novo', methods=['GET', 'POST'])
def novo_item():
    if 'usuario_logado' not in session or ['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            usuario_id = session.get('usuario_logado')
            usuario = Usuario1.query.get(usuario_id)
            if usuario:
                tipo = request.form.get('tipo')
                dia = request.form.get('dia')
                valor = request.form.get('valor')
                novo_valor = Carteira2(usuario_idusuario=usuario_id, tipo=tipo, dia=dia, valor=valor)
                db.session.add(novo_valor)
                db.session.commit()
                return redirect(url_for('home'))
            else:
                return redirect('/login')
        
        nome_pagina = "Adicionar Transação"
    return render_template('novo.html', nome_pagina=nome_pagina)

@app.route('/novo_cc', methods=['GET', 'POST'])
def novo_cc():
    if 'usuario_logado' not in session or ['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            usuario_id = session.get('usuario_logado')
            usuario = Usuario1.query.get(usuario_id)
            if usuario:
                banco = request.form.get('banco')
                bandeira = request.form.get('bandeira')
                lastd = request.form.get('lastd')
                limite = request.form.get('limite')
                validade = request.form.get('validade')
                novo_cc = Cc1(usuario_idusuario=usuario_id, banco=banco, bandeira=bandeira, lastd=lastd, limite=limite, validade=validade)
                db.session.add(novo_cc)
                db.session.commit()
                return redirect(url_for('home'))
            else:
                return redirect('/login')
        
        nome_pagina = "Adicionar Cartão de Crédito"
    return render_template('novo_cc.html', nome_pagina=nome_pagina)

# EDITAR INFORMAÇÕES SALVAS
@app.route('/edit/<int:id>', methods=["GET", 'POST'])
def editar_item(id):
    if 'usuario_logado' not in session or ['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:    
        item_para_editar = Carteira2.query.get(id)
        if request.method == 'POST':
            item_para_editar.nome = request.form.get('nome')
            item_para_editar.dia = request.form.get('dia')
            item_para_editar.valor = request.form.get('valor')
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('editar.html', item=item_para_editar)

@app.route('/edit_cc/<int:id>', methods=["GET", 'POST'])
def editar_cc(id):
    if 'usuario_logado' not in session or ['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:    
        item_para_editar = Cc1.query.get(id)
        if request.method == 'POST':
            item_para_editar.banco = request.form.get('banco')
            item_para_editar.bandeira = request.form.get('bandeira')
            item_para_editar.listd = request.form.get('listd')
            item_para_editar.limite = request.form.get('limite')
            item_para_editar.validade = request.form.get('validade')
            db.session.commit()
            return redirect(url_for('cc'))
    return render_template('editar_cc.html', item=item_para_editar)

# APAGAR INFORMAÇÕES SALVAS
@app.route('/excluir/<int:id>', methods=['POST', ])
def excluir_item(id):
    if 'usuario_logado' not in session or ['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:
        item_remover = Carteira2.query.get(id)
        if item_remover:
            db.session.delete(item_remover)
            db.session.commit()
    return redirect(url_for('home'))

@app.route('/excluir_cc/<int:id>', methods=['GET', 'POST', ])
def excluir_cc(id):
    if 'usuario_logado' not in session or ['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:
        item_remover = Cc1.query.get(id)
        if item_remover:
            db.session.delete(item_remover)
            db.session.commit()
    return redirect(url_for('cc'))

# START DA APLICAÇÃO
if __name__ == '__main__':
    app.run(debug=True)