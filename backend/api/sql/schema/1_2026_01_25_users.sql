-- +goose Up
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP NULL DEFAULT now(),
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL DEFAULT 'unset'
);
-- +goose Down
DROP TABLE users;