package routing

import (
	"encoding/json"
	"net/http"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/constants"
)

type ErrorResponse struct {
	Error  string `json:"error"`
	Status int    `json:"status"`
}
type SuccessResponse struct {
	Data interface{} `json:"data"`
}

func (config *ApiConfig) HandleFile(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		next.ServeHTTP(w, r)
	})
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
