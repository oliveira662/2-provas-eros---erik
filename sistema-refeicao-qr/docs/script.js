// Simula DB localStorage
let alunos = JSON.parse(localStorage.getItem('alunos')) || [];
let refeicoes = JSON.parse(localStorage.getItem('refeicoes')) || [];

function saveData() {
    localStorage.setItem('alunos', JSON.stringify(alunos));
    localStorage.setItem('refeicoes', JSON.stringify(refeicoes));
}

function findAluno(matricula) {
    return alunos.find(a => a.matricula === matricula);
}

function login() {
    const mat = document.getElementById('matricula').value;
    const aluno = findAluno(mat);
    if (!aluno) {
        alert('Cadastre primeiro!');
        showCadastro();
        return;
    }
    if (!aluno.aprovado) {
        alert('Pendente aprovação!');
        return;
    }
    document.getElementById('nome-student').textContent = aluno.nome;
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('student-dashboard').style.display = 'block';
}

function showCadastro() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('cadastro-form').style.display = 'block';
}

function cadastro() {
    const nome = document.getElementById('nome-cad').value;
    const mat = document.getElementById('matricula-cad').value;
    const turma = document.getElementById('turma-cad').value;
    if (findAluno(mat)) {
        alert('Matrícula existe!');
        return;
    }
    alunos.push({nome, matricula: mat, turma, aprovado: false});
    saveData();
    alert('Cadastro OK! Aguarde aprovação.');
    document.getElementById('cadastro-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
}

function solicitarQR() {
    const refeicao = {id: Date.now(), confirmada: false};
    refeicoes.push(refeicao);
    saveData();
    // QR simple texto
    const qrText = `refeicao:${refeicao.id}`;
    document.getElementById('qr-section').style.display = 'block';
    document.getElementById('student-dashboard').style.display = 'none';
    document.getElementById('qr-canvas').textContent = qrText; // Simple text QR simula
}

// Admin simulado (localStorage edit manual no F12)
console.log('Admin: Abra F12 > Console > alunos[0].aprovado = true; saveData()');

