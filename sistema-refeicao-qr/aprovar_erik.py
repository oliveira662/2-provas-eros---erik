from db import *
a = get_aluno_by_matricula('66444572010')
if a:
  print(f'ERIK ID {a["id"]} aprovado={a["aprovado"]}')
  if aprovar_aluno(a['id']):
    print('✅ ERIK APROVADO COM SUCESSO!')
  else:
    print('❌ Erro aprovação')
else:
  print('❌ Cadastre ERIK primeiro')
print('Execute: python aprovar_erik.py')

