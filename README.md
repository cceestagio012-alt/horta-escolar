# Sistema da Horta Escolar

Site público para os alunos cadastrarem canteiros, grupos e registros diários da horta escolar, com fotos e relatórios em PDF.

## Hospedagem (atual)

Tudo roda na VPS compartilhada, junto com o CETIPE:

- **App**: Flask (`backend/`), servido por Gunicorn, systemd (`horta-escolar.service`)
- **Banco**: PostgreSQL local na VPS (`horta_escolar_db`)
- **Proxy**: Nginx (`horta.sistemacetipe.com.br`)
- **Caminho na VPS**: `/var/www/projetos/horta-escolar`

Esta pasta do repositório (`backend/`) é o código-fonte de referência — o deploy é feito copiando os arquivos pra VPS (sem git na VPS, mesmo padrão do CadastroPro).

### Estrutura do backend
- `backend/app/api.py` — rotas da API (`/api/canteiros`, `/api/grupos`, `/api/registros`, `/api/importar`, `/api/exportar`, `/api/limpar-tudo`)
- `backend/app/static/index.html` — frontend (fala com a API via `fetch`)
- `backend/schema.sql` — schema do PostgreSQL
- `backend/horta-escolar.service` — unidade systemd
- `backend/nginx-horta-escolar` — configuração do Nginx

### Limites de tamanho (fotos)
Fotos são comprimidas no navegador (WebP, até 700px, qualidade adaptativa) com teto de ~260KB por foto, validado também no backend, pra manter o banco leve e não pesar a VPS compartilhada. O serviço systemd também tem teto de memória (250M) e CPU (50%).

## Histórico
Anteriormente hospedado em GitHub Pages + Supabase; migrado para a VPS própria em 2026-08-26 para manter tudo centralizado e sob controle direto.
