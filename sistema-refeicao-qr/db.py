import sqlite3
import os
from datetime import date

DB_PATH = 'refeicoes.db'

def init_db():
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else '.', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT UNIQUE NOT NULL,
            turma TEXT,
            aprovado BOOLEAN DEFAULT FALSE,
            data_cadastro DATE DEFAULT (date('now'))
        )
    ''')
    
    # Adiciona coluna aprovado se não existir em tabelas antigas
    cursor.execute("PRAGMA table_info(alunos)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'turma' not in columns:
        cursor.execute('ALTER TABLE alunos ADD COLUMN turma TEXT')
    if 'aprovado' not in columns:
        cursor.execute('ALTER TABLE alunos ADD COLUMN aprovado BOOLEAN DEFAULT FALSE')
    if 'data_cadastro' not in columns:
        cursor.execute('ALTER TABLE alunos ADD COLUMN data_cadastro DATE')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS refeicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER,
            data DATE NOT NULL,
            confirmada BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (aluno_id) REFERENCES alunos (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS refeicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER,
            data DATE NOT NULL,
            confirmada BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (aluno_id) REFERENCES alunos (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def list_alunos_full():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, matricula, aprovado FROM alunos ORDER BY data_cadastro DESC')
    alunos = cursor.fetchall()
    conn.close()
    return [{'id':r[0], 'nome':r[1], 'matricula':r[2], 'aprovado':bool(r[3])} for r in alunos]

def list_pendentes_alunos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, matricula FROM alunos WHERE aprovado = FALSE ORDER BY id DESC')
    pendentes = cursor.fetchall()
    conn.close()
    return [{'id':r[0], 'nome':r[1], 'matricula':r[2]} for r in pendentes]

def aprovar_aluno(aluno_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE alunos SET aprovado = TRUE WHERE id = ?', (aluno_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def rejeitar_aluno(aluno_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_total_alunos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM alunos')
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_stats_admin():
    hoje = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM refeicoes WHERE data = ?', (hoje,))
    solicitadas = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM refeicoes WHERE data = ? AND confirmada = TRUE', (hoje,))
    confirmadas = cursor.fetchone()[0]
    taxa = round((confirmadas/solicitadas*100) if solicitadas else 0, 1)
    cursor.execute('SELECT COUNT(*) FROM alunos')
    alunos_total = cursor.fetchone()[0]
    conn.close()
    return {
        'alunos_total': alunos_total,
        'refeicoes_solicitadas': solicitadas,
        'refeicoes_confirmadas': confirmadas,
        'taxa_confirmacao': taxa
    }

def cadastrar_aluno(nome, matricula, turma=''):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO alunos (nome, matricula, turma) VALUES (?, ?, ?)', (nome, matricula, turma))
    aluno_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return aluno_id

def get_aluno_by_matricula(matricula):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, aprovado FROM alunos WHERE matricula = ?', (matricula,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'nome': row[1], 'aprovado': bool(row[2])}
    return None

def solicitar_refeicao(aluno_id):
    hoje = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO refeicoes (aluno_id, data) VALUES (?, ?)', (aluno_id, hoje))
    refeicao_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return refeicao_id

def confirmar_refeicao(refeicao_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE refeicoes SET confirmada = TRUE WHERE id = ?', (refeicao_id,))
    conn.commit()
    conn.close()

def get_refeicoes_hoje():
    hoje = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, a.nome, a.matricula, r.confirmada 
        FROM refeicoes r JOIN alunos a ON r.aluno_id = a.id 
        WHERE r.data = ? ORDER BY r.id
    ''', (hoje,))
    refeicoes = cursor.fetchall()
    conn.close()
    return refeicoes

def get_total_confirmadas_hoje():
    hoje = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM refeicoes WHERE data = ? AND confirmada = TRUE', (hoje,))
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_refeicoes_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT data, COUNT(*) as solicitadas, SUM(CASE WHEN confirmada THEN 1 ELSE 0 END) as confirmadas FROM refeicoes GROUP BY data ORDER BY data DESC LIMIT 7')
    rows = cursor.fetchall()
    conn.close()
    relatorios = []
    for r in rows:
        solicitadas = r[1]
        confirmadas = r[2]
        taxa = round((confirmadas/solicitadas*100) if solicitadas else 0, 1)
        relatorios.append({'data': r[0], 'solicitadas': solicitadas, 'confirmadas': confirmadas, 'taxa': taxa})
    return relatorios
