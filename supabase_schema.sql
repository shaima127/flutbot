-- 1. Enable pgvector extension (optional if using local FAISS first, but recommended for production)
create extension if not exists vector;

-- 2. Create users table for progress tracking
create table if not exists users (
    id uuid default gen_random_uuid() primary key,
    whatsapp_number text unique not null,
    level text default 'beginner',
    current_lesson int default 0,
    score int default 0,
    status text default 'testing', -- testing, learning, expert
    created_at timestamp with time zone default now(),
    last_active timestamp with time zone default now()
);

-- 3. Create lessons table (optional if RAG handles all, but good for structured content)
create table if not exists lessons (
    id serial primary key,
    level text,
    title text,
    content text,
    code_snippets text[]
);
