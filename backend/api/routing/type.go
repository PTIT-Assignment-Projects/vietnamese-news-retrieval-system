package routing

import (
	"database/sql"
	"encoding/json"
	"net/http"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/constants"
	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/database"
)

type ApiConfig struct {
	Db        *sql.DB
	Queries   *database.Queries
	JwtSecret string
}

func RespondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	w.Header().Set(constants.ContentType, constants.MediaTypeJson)
	w.WriteHeader(code)
	data := SuccessResponse{
		Data: payload,
	}
	_ = json.NewEncoder(w).Encode(data)
}

func RespondWithError(w http.ResponseWriter, code int, msg string) {
	RespondWithJSON(w, code, ErrorResponse{
		Error:  msg,
		Status: code,
	})
}
func ResponseWithStatus(w http.ResponseWriter, code int) {
	w.WriteHeader(code)
}
