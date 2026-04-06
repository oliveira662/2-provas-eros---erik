from flask import Flask, render_template, request, redirect, url_for, flash, session
import qrcode
from io import BytesIO
import base64
from db import *

app = Flask(__name__)
app.secret_key = 'mvp_refeicao_qr_secret'

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

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['user'] == 'Erik XTech' and request.form['pass'] == 'Er!k_XT3ch@9#7$2Qp':
            session['admin'] = True
            return redirect(url_for('admin'))
        flash('Credenciais inválidas!')
    return render_template('admin/login.html')

@app.route('/admin/aprovar/<int:aluno_id>')
def admin_aprovar(aluno_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if aprovar_aluno(aluno_id):
        flash('Aluno aprovado!')
    else:
        flash('Erro ao aprovar aluno')
    return redirect(url_for('admin'))

@app.route('/admin/rejeitar/<int:aluno_id>')
def admin_rejeitar(aluno_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if rejeitar_aluno(aluno_id):
        flash('Cadastro rejeitado!')
    else:
        flash('Erro ao rejeitar')
    return redirect(url_for('admin'))

@app.route('/admin')
@app.route('/admin/alunos')
@app.route('/admin/relatorios')
def admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    stats = get_stats_admin()
    alunos = list_alunos_full()
    pendentes = list_pendentes_alunos()
    refeicoes = get_refeicoes_data()
    return render_template('admin/dashboard.html', stats=stats, alunos=alunos, pendentes=pendentes, refeicoes=refeicoes)

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/report')
def report():
    total_confirmadas = get_total_confirmadas_hoje()
    refeicoes = get_refeicoes_hoje()
    return render_template('report.html', total_confirmadas=total_confirmadas, refeicoes=refeicoes)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
