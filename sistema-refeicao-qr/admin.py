from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import list_alunos_full as list_alunos, get_stats_admin, get_refeicoes_data
import csv
from io import StringIO

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

ADMIN_CREDENTIALS = {'admin': generate_password_hash('123456')}

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in ADMIN_CREDENTIALS and check_password_hash(ADMIN_CREDENTIALS[username], password):
            user = AdminUser(username)
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Credenciais inválidas!')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@admin_bp.route('/')
@login_required
def dashboard():
    stats = get_stats_admin()
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/alunos')
@login_required
def alunos():
    alunos = list_alunos()
    return render_template('admin/alunos.html', alunos=alunos)

@admin_bp.route('/relatorios')
@login_required
def relatorios():
    relatorios = get_refeicoes_data()
    return render_template('admin/relatorios.html', relatorios=relatorios)

@admin_bp.route('/export_csv')
@login_required
def export_csv():
    relatorios = get_refeicoes_data()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Data', 'Solicitadas', 'Confirmadas', 'Taxa%'])
    for r in relatorios:
        cw.writerow([r['data'], r['solicitadas'], r['confirmadas'], r['taxa']])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=relatorios.csv"
    output.headers["Content-type"] = "text/csv"
    return output
