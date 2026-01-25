-- name: CreateRefreshToken :one
INSERT INTO refresh_tokens (token, user_id, expires_at, created_at, updated_at)
VALUES ($1, $2, $3, NOW(), NOW())
    RETURNING token, created_at, updated_at, user_id, expires_at, revoked_at;


-- name: GetUserFromRefreshToken :one
SELECT users.id, users.created_at, users.updated_at, users.email, users.name
FROM refresh_tokens
         JOIN users ON users.id = refresh_tokens.user_id
WHERE refresh_tokens.token = $1
  AND refresh_tokens.expires_at > now()
  AND refresh_tokens.revoked_at IS NULL;

-- name: RevokeRefreshToken :exec
UPDATE refresh_tokens
SET revoked_at = now(), updated_at = now()
WHERE token = $1;

-- name: GetRefreshTokenFromUser :one
SELECT refresh_tokens.token
FROM refresh_tokens
JOIN users ON users.id = refresh_tokens.user_id
WHERE refresh_tokens.user_id = $1
  AND refresh_tokens.expires_at > now()
  AND refresh_tokens.revoked_at IS NULL;