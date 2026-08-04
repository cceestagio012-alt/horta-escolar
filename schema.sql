-- Schema do Sistema da Horta Escolar (Supabase / Postgres)
create extension if not exists pgcrypto;

create table if not exists canteiros (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  cultura text not null,
  data date not null,
  colheita date,
  obs text,
  created_at timestamptz not null default now()
);

create table if not exists grupos (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  turma text not null,
  integrantes text not null,
  canteiro_id uuid references canteiros(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists registros (
  id uuid primary key default gen_random_uuid(),
  data date not null,
  aluno text not null,
  turma text not null,
  grupo_id uuid references grupos(id) on delete set null,
  canteiro_id uuid references canteiros(id) on delete set null,
  irrigacao text,
  solo text,
  crescimento text,
  altura numeric,
  pragas text,
  capina text,
  adubacao text,
  obs text,
  foto text,
  created_at timestamptz not null default now()
);

alter table canteiros enable row level security;
alter table grupos enable row level security;
alter table registros enable row level security;

-- Acesso publico total (sem login), conforme decidido para uso livre pelos alunos.
create policy "public_all_canteiros" on canteiros for all using (true) with check (true);
create policy "public_all_grupos" on grupos for all using (true) with check (true);
create policy "public_all_registros" on registros for all using (true) with check (true);
