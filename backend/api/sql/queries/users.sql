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