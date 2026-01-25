package routing

import "net/http"

func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	ResponseWithJSON(w, http.StatusOK, "OK")
}
