-- Idempotent Tiger Cloud / Postgres Schema Migration
-- Enables pgvector and TimescaleDB extensions, creates code_chunks and repo_file_index tables.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Memory Lane: Repository code chunks for hybrid vector + keyword search
CREATE TABLE IF NOT EXISTS code_chunks (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    repo         TEXT         NOT NULL,
    path         TEXT         NOT NULL,
    symbol       TEXT,                       -- function/class name (nullable)
    chunk_index  INT          NOT NULL,      -- order within file
    content      TEXT         NOT NULL,
    embedding    VECTOR(256)  NOT NULL,      -- text-embedding-3-large, 256 dims
    token_count  INT,
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT code_chunks_unique_idx UNIQUE (repo, path, chunk_index)
);

-- Full-Text Search GIN index
ALTER TABLE code_chunks
    ADD COLUMN IF NOT EXISTS content_tsv TSVECTOR
        GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX IF NOT EXISTS code_chunks_fts_idx
    ON code_chunks USING GIN (content_tsv);

CREATE INDEX IF NOT EXISTS code_chunks_repo_path_idx
    ON code_chunks (repo, path);

-- Repository File Index for Freshness Tracking
CREATE TABLE IF NOT EXISTS repo_file_index (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    repo             TEXT         NOT NULL,
    path             TEXT         NOT NULL,
    file_sha         TEXT         NOT NULL,
    last_commit_sha  TEXT         NOT NULL,
    chunk_count      INT          NOT NULL DEFAULT 0,
    last_indexed_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT repo_file_index_unique UNIQUE (repo, path)
);
