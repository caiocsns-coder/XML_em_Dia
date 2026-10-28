# XML em Dia

Ferramentas gratuitas para conferir a **NFS-e padrão nacional** e as tabelas do **IBS/CBS** antes de enviar.
Tudo roda no navegador: nenhum XML sai do computador de quem usa.

| Página | O que faz |
|---|---|
| `index.html` | Página inicial: ferramentas, privacidade, planos e contato para o diagnóstico |
| `validador.html` | Valida DPS, RPS e NFS-e contra o XSD, as regras oficiais `Exxxx` e os Anexos VII e VIII |
| `consulta.html` | Consulta item da LC 116 × NBS × `cIndOp` × `cClassTrib` (Anexos VII e VIII) |

## Publicar no GitHub Pages

1. Crie o repositório `xml-em-dia` (público) e suba estes arquivos na branch `main`.
2. Em `config.json`, troque `SEU-USUARIO` pelo seu usuário e rode `python3 construir.py`.
3. Em *Settings → Pages*, escolha *Deploy from a branch*, `main` e `/ (root)`.
4. O site fica em `https://SEU-USUARIO.github.io/xml-em-dia/`.

## Como o site é montado

```text
src/index.html              página inicial (edite aqui)
src/consulta.template.html  página da consulta, sem os dados
src/validador.base.html     index.html do build público do validador
construir.py                monta index.html, validador.html e consulta.html na raiz
config.json                 endereço do repositório (vai para o rodapé e as metatags)
```

Os arquivos da raiz são gerados, mas ficam no git para o Pages servir sem build.
O workflow `verificar.yml` reprova o push se eles estiverem diferentes do que `src/` produz.

## Atualizar quando sair NT, XSD ou Anexo novo

```bash
# 1. regere o validador público, como de costume
python construir_publico.py --fonte ... --saida ../publico-github ...

# 2. traga o index.html novo e remonte o site
python3 construir.py --validador ../publico-github/index.html

# 3. publique
git add -A && git commit -m "Atualiza referências" && git push
```

A consulta lê os Anexos VII e VIII de dentro do validador, então as duas páginas ficam sempre na mesma versão.

## Varredura de termos (opcional, local)

Crie um `proibidos.txt` na raiz, com um termo ou regex por linha. Ele está no `.gitignore`, então não vai para o repositório.
Quando existe, `construir.py` reprova o build se algum termo aparecer nos arquivos gerados.

## Aviso

Ferramenta independente, não afiliada à Receita Federal, ao Comitê Gestor da NFS-e nem ao Serpro. Não substitui a validação
do ambiente nacional nem constitui orientação tributária.

## Licença

[MIT](LICENSE). Os documentos oficiais lidos pelas ferramentas pertencem aos seus publicadores.
