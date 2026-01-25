-- +goose Up
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP NULL ,
    email TEXT NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    password TEXT NOT NULL DEFAULT 'unset'
);
-- +goose Down
DROP TABLE IF EXISTS users;