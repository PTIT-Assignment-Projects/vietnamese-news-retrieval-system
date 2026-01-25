-- name: CreateUser :one
INSERT INTO users (id, created_at, updated_at, name, email, password)
VALUES (
           gen_random_uuid(),
           NOW(),
           NOW(),
        $1,
           $2,
           $3
       )
    RETURNING id, created_at, updated_at, name, email;

-- name: GetUserByEmail :one
SELECT id, name, email, created_at, updated_at, password
FROM users
WHERE email = $1;
-- name: GetUserByID :one
SELECT id, name, email, created_at, updated_at
FROM users
WHERE id = $1;