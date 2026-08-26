-- Schema do Sistema da Horta Escolar (PostgreSQL na VPS)
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
