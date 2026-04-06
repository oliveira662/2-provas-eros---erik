# Sistema Refeição QR Code

## Funcionalidades
- Cadastro aluno (pendente aprovação admin)
- Login aprovado → Student dashboard → Solicitar refeição (QR)
- Cantina: Scanner QR → Confirmar
- Admin: Aprovar/rejeitar, dashboard stats, relatórios CSV

## Instalação
```bash
cd sistema-refeicao-qr
pip install -r requirements.txt
```

## Rodar
```bash
python app.py
```
Acesse http://127.0.0.1:5000/

**Admin:** /admin/login → user: `admin` pass: `123456`

**DB:** refeicoes.db auto-criada.

## Estrutura
- app.py: Rotas principais + blueprint admin
- db.py: SQLite alunos/refeicoes
- templates/: HTML Jinja2
- static/: CSS/JS + html5-qrcode.min.js

TODO.md para pendentes.
