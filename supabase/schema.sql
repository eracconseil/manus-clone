-- ManusClone — Schéma Supabase
-- Exécuter dans l'éditeur SQL de Supabase

-- Extension pour UUIDs
create extension if not exists "pgcrypto";

-- ─────────────────────────────────────────────────────────────
-- Table : profiles (lie auth.users aux plans SaaS)
-- ─────────────────────────────────────────────────────────────
create table if not exists profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  email        text,
  plan         text not null default 'free',   -- free | pro | business
  tasks_used   int  not null default 0,
  tasks_limit  int  not null default 10,
  stripe_customer_id      text,
  stripe_subscription_id  text,
  billing_period_start    timestamptz default now(),
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

-- Auto-create profile on signup
create or replace function handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_user();

-- ─────────────────────────────────────────────────────────────
-- Table : sessions (conversations)
-- ─────────────────────────────────────────────────────────────
create table if not exists sessions (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid references profiles(id) on delete cascade,
  title      text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- ─────────────────────────────────────────────────────────────
-- Table : messages
-- ─────────────────────────────────────────────────────────────
create table if not exists messages (
  id          uuid primary key default gen_random_uuid(),
  session_id  uuid references sessions(id) on delete cascade,
  role        text not null check (role in ('user', 'assistant')),
  content     text not null,
  model       text,             -- qwen | kimi | claude
  tokens_in   int  default 0,
  tokens_out  int  default 0,
  cost_usd    numeric(10,6) default 0,
  created_at  timestamptz default now()
);

-- ─────────────────────────────────────────────────────────────
-- Table : task_runs (une exécution = un appel agent)
-- ─────────────────────────────────────────────────────────────
create table if not exists task_runs (
  id          uuid primary key default gen_random_uuid(),
  session_id  uuid references sessions(id) on delete cascade,
  user_id     uuid references profiles(id) on delete cascade,
  model       text,
  complexity  text,
  tokens_in   int  default 0,
  tokens_out  int  default 0,
  cost_usd    numeric(10,6) default 0,
  tool_calls  int  default 0,
  duration_ms int  default 0,
  created_at  timestamptz default now()
);

-- ─────────────────────────────────────────────────────────────
-- RLS (Row Level Security)
-- ─────────────────────────────────────────────────────────────
alter table profiles  enable row level security;
alter table sessions  enable row level security;
alter table messages  enable row level security;
alter table task_runs enable row level security;

-- Profiles : lecture/mise à jour par l'utilisateur lui-même
create policy "profiles: self read"   on profiles for select using (auth.uid() = id);
create policy "profiles: self update" on profiles for update using (auth.uid() = id);

-- Sessions
create policy "sessions: own"   on sessions for all using (auth.uid() = user_id);

-- Messages
create policy "messages: own"   on messages for all
  using (session_id in (select id from sessions where user_id = auth.uid()));

-- Task runs
create policy "task_runs: own"  on task_runs for all using (auth.uid() = user_id);

-- ─────────────────────────────────────────────────────────────
-- Index
-- ─────────────────────────────────────────────────────────────
create index if not exists idx_sessions_user    on sessions(user_id, created_at desc);
create index if not exists idx_messages_session on messages(session_id, created_at);
create index if not exists idx_task_runs_user   on task_runs(user_id, created_at desc);

-- ─────────────────────────────────────────────────────────────
-- Fonction : incrémenter tasks_used et vérifier la limite
-- ─────────────────────────────────────────────────────────────
create or replace function increment_task_usage(p_user_id uuid)
returns boolean language plpgsql security definer as $$
declare
  v_used  int;
  v_limit int;
begin
  select tasks_used, tasks_limit into v_used, v_limit
  from profiles where id = p_user_id;

  if v_used >= v_limit then
    return false;  -- limite atteinte
  end if;

  update profiles
  set tasks_used = tasks_used + 1, updated_at = now()
  where id = p_user_id;

  return true;
end;
$$;

-- Fonction : reset mensuel (à appeler via cron ou webhook Stripe)
create or replace function reset_monthly_usage()
returns void language plpgsql security definer as $$
begin
  update profiles
  set tasks_used = 0, billing_period_start = now(), updated_at = now()
  where billing_period_start < now() - interval '30 days';
end;
$$;
