from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import MySQLdb.cursors
import locale

# INICIALIZAÇÃO DA APLICAÇÃO
app = Flask(__name__)

# CHAVE DE SEGURANÇA DA APLICAÇÃO
app.secret_key = 'empada'

# CONEXÃO COM O BANCO DE DADOS
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'frederico'
app.config['MYSQL_PASSWORD'] = 'Dequi.5812'
app.config['MYSQL_DB'] = 'teste_carteira'
mysql = MySQL(app)

# Configuração do Locale para reconhecer o REAL
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# ROTA PRINCIPAL
@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM teste_carteira.carteira1') 
    dados_carteira = cursor.fetchall()
    cursor.close()
    # Formatando os valores para REAL
    for item in dados_carteira:
        item['valor'] = locale.currency(item['valor'], grouping=True)
    return render_template('app.html', carteira=dados_carteira)

# ADICIONAR NOVAS INFORMAÇÕES
@app.route('/novo')
def novo_item():
    return render_template('novo.html')

@app.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        dia = request.form.get('dia')
        valor = request.form.get('valor')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('INSERT INTO carteira1 VALUES (NULL, % s, % s, % s)', (nome, dia, valor, )) 
        mysql.connection.commit()
    return redirect(url_for('index'))

# EDITAR INFORMAÇÕES SALVAS
@app.route('/edit/<int:id>', methods=["GET", 'POST'])
def modificar_item(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM carteira1 WHERE id=%s', (id,))
    dados_item = cursor.fetchone()
    cursor.close()
    return render_template('editar.html', item=dados_item)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_item(id):
    if request.method == 'POST':
        nome = request.form.get('nome')
        dia = request.form.get('dia')
        valor = request.form.get('valor')
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE carteira1 SET nome=%s, dia=%s, valor=%s WHERE id=%s', (nome, dia, valor, id))
        mysql.connection.commit()
        cursor.close()
    return redirect('/')

# APAGAR INFORMAÇÕES SALVAS
@app.route('/excluir/<int:id>', methods=['POST', ])
def excluir_item(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM carteira1 WHERE id=%s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('index'))

# START DA APLICAÇÃO
if __name__ == '__main__':
    app.run(debug=True)