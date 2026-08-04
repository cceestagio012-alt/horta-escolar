# Sistema da Horta Escolar

Site público para os alunos cadastrarem canteiros, grupos e registros diários da horta escolar, com fotos e relatórios em PDF.

Os dados ficam salvos em um banco de dados compartilhado no [Supabase](https://supabase.com) — qualquer aluno com o link vê e lança dados, sem necessidade de login.

## Estrutura

- `index.html` — todo o site (HTML, CSS e JavaScript).
- `schema.sql` — script para criar as tabelas no Supabase (`canteiros`, `grupos`, `registros`).
- `manifest.json` / `service-worker.js` — permitem instalar o site como app (PWA) no celular.

## Publicação

O site é hospedado pelo GitHub Pages, publicado a partir da branch `main`.

## Acesso ao banco

⚠️ Como o acesso é livre (sem login), qualquer pessoa com o link do site pode ler, criar, editar e apagar dados. Isso foi uma escolha consciente para facilitar o uso em sala. Se no futuro for necessário restringir, adicionar autenticação no Supabase e ajustar as políticas de RLS em `schema.sql`.
