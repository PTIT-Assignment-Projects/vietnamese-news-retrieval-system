package routing

import (
	"database/sql"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/database"
)

type ApiConfig struct {
	Db        *sql.DB
	Queries   *database.Queries
	JwtSecret string
}
