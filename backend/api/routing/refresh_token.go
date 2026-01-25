package routing

import (
	"net/http"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/auth"
)

// STRUCT
type getTokenFromRefreshToken struct {
	Token string `json:"token"`
}

// POST /api/v1/auth/refresh
func (config *ApiConfig) HandleCreateTokenByRefreshToken(w http.ResponseWriter, r *http.Request) {
	refreshToken, err := auth.GetBearerToken(r.Header)
	if err != nil {
		ResponseWithError(w, http.StatusUnauthorized, err.Error())
		return
	}
	user, err := config.Queries.GetUserFromRefreshToken(r.Context(), refreshToken)
	if err != nil {
		ResponseWithError(w, http.StatusUnauthorized, err.Error())
		return
	}
	token, err := CreateToken(user.ID, config.JwtSecret)
	if err != nil {
		ResponseWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	ResponseWithJSON(w, http.StatusOK, getTokenFromRefreshToken{
		Token: token,
	})
}

// POST /api/v1/auth/logout
func (config *ApiConfig) HandleRevokeRefreshToken(w http.ResponseWriter, r *http.Request) {
	refreshToken, err := auth.GetBearerToken(r.Header)
	if err != nil {
		ResponseWithError(w, http.StatusUnauthorized, err.Error())
		return
	}
	err = config.Queries.RevokeRefreshToken(r.Context(), refreshToken)
	if err != nil {
		ResponseWithError(w, http.StatusBadRequest, err.Error())
		return
	}
	ResponseWithStatus(w, http.StatusNoContent)
}
