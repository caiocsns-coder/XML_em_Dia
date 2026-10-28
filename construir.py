#!/usr/bin/env python3
"""
Monta o site a partir de src/:

  index.html      página inicial (cópia de src/index.html)
  validador.html  validador da NFS-e (src/validador.base.html + link de volta ao portal + endereço do repositório)
  consulta.html   consulta aos Anexos VII e VIII (src/consulta.template.html + dados lidos do próprio validador)

Uso:
  python3 construir.py                         # monta os três arquivos na raiz
  python3 construir.py --validador CAMINHO     # antes, copia um index.html novo do validador para src/
  python3 construir.py --verificar             # só confere se os arquivos da raiz estão em dia (usado no CI)

Opcional: se existir o arquivo proibidos.txt (um termo ou regex por linha; fica fora do git),
o build é reprovado quando algum termo aparecer nos arquivos gerados.
"""
import argparse, json, os, re, shutil, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(RAIZ, 'src')
CONFIG = os.path.join(RAIZ, 'config.json')


def ler(p):
    with open(p, encoding='utf8') as f:
        return f.read()


def config():
    c = json.loads(ler(CONFIG)) if os.path.exists(CONFIG) else {}
    repo = c.get('repo', 'https://github.com/SEU-USUARIO/xml-em-dia').rstrip('/')
    m = re.search(r'github\.com/([^/]+)/([^/]+)', repo)
    pages = c.get('pages') or (f'https://{m.group(1).lower()}.github.io/{m.group(2)}/' if m else '')
    return repo, pages


def exigir(txt, velho, novo, rotulo):
    n = txt.count(velho)
    if n != 1:
        sys.exit(f'FALHA: "{rotulo}" casou {n} vez(es); esperado 1. O validador mudou?')
    return txt.replace(velho, novo, 1)


def montar_validador(base, repo, pages):
    t = base
    t = exigir(t, '<h1>Comparador de tags da NFS-e</h1>',
               '<a href="index.html" style="color:#F8DFC9;font-weight:600;font-size:13px;text-decoration:none;white-space:nowrap">&larr; XML em Dia</a>\n'
               '    <h1>Comparador de tags da NFS-e</h1>', 'título do topo')
    t = exigir(t, '<title>Comparador de tags da NFS-e</title>', '<title>Validador NFS-e</title>', 'título da página')
    t = re.sub(r'https://seu-usuario\.github\.io/SEU-REPOSITORIO/', pages + 'validador.html', t, flags=re.I)
    t = t.replace('https://github.com/SEU-USUARIO/SEU-REPOSITORIO', repo)
    return t


def montar_consulta(base, modelo):
    m = re.search(r'window\.REFERENCIAS_EMBUTIDAS = (\{.*?\});\n', base, re.S)
    if not m:
        sys.exit('FALHA: biblioteca de referências não encontrada no validador.')
    ref = json.loads(m.group(1))
    a7, a8 = ref.get('anexoVII'), ref.get('anexoVIII')
    if not a7 or not a8:
        sys.exit('FALHA: o validador não traz os Anexos VII e VIII.')
    dados = {
        # cIndOp: [código, tipo, característica, local, dispositivo, indNFSe, local de incidência do IBS]
        'a7': [[l[0], l[1], l[2], l[3], l[4], l[7], l[9]] for l in a7['linhas']],
        # combinações: [item LC 116, NBS, cIndOp, cClassTrib, local]
        'a8': [l[:5] for l in a8['linhas']],
        'itens': a8['itens'], 'cclass': a8['cclass'],
    }
    blob = json.dumps(dados, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    t = exigir(modelo, '__DADOS__', blob, 'marcador de dados')
    t = t.replace('__V7__', a7.get('versao', '?')).replace('__V8__', a8.get('versao', '?'))
    return t, len(a8['linhas']), len(a7['linhas'])


def varrer(saidas):
    p = os.path.join(RAIZ, 'proibidos.txt')
    if not os.path.exists(p):
        return
    termos = [l.strip() for l in ler(p).splitlines() if l.strip() and not l.startswith('#')]
    achados = []
    for nome, txt in saidas.items():
        for pat in termos:
            for mm in re.finditer(pat, txt, flags=re.I):
                ini = max(0, mm.start() - 40)
                achados.append(f'  {nome}: /{pat}/  …{txt[ini:mm.end() + 40]}…'.replace('\n', ' '))
    if achados:
        print('REPROVADO na varredura de termos proibidos:')
        print('\n'.join(achados[:30]))
        sys.exit(1)
    print(f'Varredura: {len(termos)} termos, nenhum encontrado.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--validador', help='index.html gerado pelo build público do validador')
    ap.add_argument('--verificar', action='store_true')
    a = ap.parse_args()

    if a.validador:
        shutil.copy(a.validador, os.path.join(SRC, 'validador.base.html'))
        print('Validador atualizado em src/validador.base.html')

    repo, pages = config()
    base = ler(os.path.join(SRC, 'validador.base.html'))
    consulta, n8, n7 = montar_consulta(base, ler(os.path.join(SRC, 'consulta.template.html')))
    saidas = {
        'index.html': ler(os.path.join(SRC, 'index.html')),
        'validador.html': montar_validador(base, repo, pages),
        'consulta.html': consulta,
    }

    if a.verificar:
        fora = [n for n, t in saidas.items()
                if not os.path.exists(os.path.join(RAIZ, n)) or ler(os.path.join(RAIZ, n)) != t]
        if fora:
            sys.exit('Desatualizado: ' + ', '.join(fora) + '. Rode python3 construir.py e faça commit.')
        print('Arquivos da raiz em dia com src/.')
        return

    varrer(saidas)
    for nome, txt in saidas.items():
        with open(os.path.join(RAIZ, nome), 'w', encoding='utf8') as f:
            f.write(txt)
    print(f'Montados index.html, validador.html e consulta.html ({n8} combinações do Anexo VIII, {n7} cIndOp).')


if __name__ == '__main__':
    main()
