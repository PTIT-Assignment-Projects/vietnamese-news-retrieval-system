package routing

import (
	"net/http"
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
