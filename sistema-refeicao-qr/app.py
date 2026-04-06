from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager
from flask_login import LoginManager
import qrcode
from io import BytesIO
import base64
from db import *
from admin import admin_bp

app = Flask(__name__)
app.secret_key = 'mvp_refeicao_qr_secret'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login'

@login_manager.user_loader
def load_user(user_id):
    from admin import AdminUser
    return AdminUser(user_id)

app.register_blueprint(admin_bp)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return login()
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        turma = request.form.get('turma', '')
        aluno = get_aluno_by_matricula(matricula)
        if aluno:
            flash('Matrícula já cadastrada! Use outra ou contate admin.')
            return render_template('cadastro.html')
        try:
            cadastrar_aluno(nome, matricula, turma)
            flash('Cadastro realizado com sucesso! Aguarde aprovação do admin.')
        except Exception as e:
            flash('Erro no cadastro. Tente novamente.')
            return render_template('cadastro.html')
        return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/login', methods=['POST'])
def login():
    matricula = request.form['matricula']
    aluno = get_aluno_by_matricula(matricula)
    if not aluno:
        flash('Faça cadastro primeiro!')
        return redirect(url_for('index'))
    if not aluno['aprovado']:
        flash('Cadastro pendente de aprovação!')
        return redirect(url_for('index'))
    nome = aluno['nome']
    return redirect(url_for('student', aluno_id=aluno['id'], nome=nome))

@app.route('/student/<int:aluno_id>')
def student(aluno_id):
    nome = request.args.get('nome', 'Aluno')
    return render_template('student.html', aluno_id=aluno_id, nome=nome)

@app.route('/solicitar/<int:aluno_id>')
def solicitar(aluno_id):
    refeicao_id = solicitar_refeicao(aluno_id)
    qr_data = f"refeicao:{refeicao_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return render_template('qr.html', qr_data=base64.b64encode(img_buffer.read()).decode(), refeicao_id=refeicao_id)

@app.route('/cantina')
def cantina():
    refeicoes = get_refeicoes_hoje()
    total_confirmadas = get_total_confirmadas_hoje()
    return render_template('cantina.html', refeicoes=refeicoes, total_confirmadas=total_confirmadas)

@app.route('/confirmar/<int:refeicao_id>')
def confirmar(refeicao_id):
    confirmar_refeicao(refeicao_id)
    return redirect(url_for('cantina'))





@app.route('/report')
def report():
    total_confirmadas = get_total_confirmadas_hoje()
    refeicoes = get_refeicoes_hoje()
    return render_template('report.html', total_confirmadas=total_confirmadas, refeicoes=refeicoes)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
