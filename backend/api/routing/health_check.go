package routing

import "net/http"

func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	RespondWithJSON(w, http.StatusOK, "OK")
}
