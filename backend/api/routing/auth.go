package routing

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/auth"
	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/constants"
	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/database"
	"github.com/google/uuid"
)

// STRUCT
type loginUser struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}
type loginUserResponse struct {
	ID           string    `json:"id"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	Email        string    `json:"email"`
	Name         string    `json:"name"`
	Token        string    `json:"token"`
	RefreshToken string    `json:"refresh_token"`
}
type fetchAccountResponse struct {
	ID        string    `json:"id"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	Email     string    `json:"email"`
	Name      string    `json:"name"`
}

// HANDLER
func (config *ApiConfig) HandleLogin(w http.ResponseWriter, r *http.Request) {
	var request loginUser
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		ResponseWithError(w, http.StatusBadRequest, constants.InvalidRequestBody)
		return
	}
	user, err := config.Queries.GetUserByEmail(r.Context(), request.Email)
	if err != nil {
		ResponseWithError(w, http.StatusBadRequest, fmt.Sprintf("%s: %s", constants.CannotFindUserWithEmail, request.Email))
		return
	}
	isMatch, err := auth.CheckHashedPassword(request.Password, user.Password)
	if err != nil {
		ResponseWithError(w, http.StatusInternalServerError, fmt.Sprintf("%s: %s", constants.ErrorValidatingPassword, err.Error()))
		return
	}
	if !isMatch {
		ResponseWithError(w, http.StatusUnauthorized, constants.PasswordNotMatch)
		return
	}
	token, err := CreateToken(user.ID, config.JwtSecret)
	var refreshToken string
	refreshToken, err = config.Queries.GetRefreshTokenFromUser(r.Context(), user.ID)
	if err != nil {
		refreshToken, err = auth.MakeRefreshToken()
		if err != nil {
			ResponseWithError(w, http.StatusInternalServerError, fmt.Sprintf("%s:%s", constants.ErrorCreatingRefreshToken, err.Error()))
			return
		}
		params := database.CreateRefreshTokenParams{
			Token:     refreshToken,
			UserID:    user.ID,
			ExpiresAt: time.Now().Add(time.Minute * 60 * 24 * 60),
		}
		_, err = config.Queries.CreateRefreshToken(r.Context(), params)
		if err != nil {
			ResponseWithError(w, http.StatusInternalServerError, err.Error())
			return
		}
	}
	ResponseWithJSON(w, http.StatusOK, mapUserToLoginUserResponse(user, token, refreshToken))
}
func (config *ApiConfig) HandleFetchAccount(w http.ResponseWriter, r *http.Request) {
	userId, err := CheckValidToken(r, config.JwtSecret)
	if err != nil {
		ResponseWithError(w, http.StatusUnauthorized, err.Error())
		return
	}
	user, err := config.Queries.GetUserByID(r.Context(), userId)
	if err != nil {
		ResponseWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	ResponseWithJSON(w, http.StatusOK, mapToFetchAccountResponse(user))
}

// MAPPER
func mapUserToLoginUserResponse(user database.GetUserByEmailRow, token, refreshToken string) loginUserResponse {
	return loginUserResponse{
		ID:           user.ID.String(),
		CreatedAt:    user.CreatedAt,
		UpdatedAt:    user.UpdatedAt,
		Name:         user.Name,
		Email:        user.Email,
		Token:        token,
		RefreshToken: refreshToken,
	}
}
func mapToFetchAccountResponse(user database.GetUserByIDRow) fetchAccountResponse {
	return fetchAccountResponse{
		ID:        user.ID.String(),
		CreatedAt: user.CreatedAt,
		UpdatedAt: user.UpdatedAt,
		Name:      user.Name,
		Email:     user.Email,
	}
}

// HELPER
func CreateToken(userId uuid.UUID, tokenSecret string) (string, error) {
	return auth.CreateJWT(userId, tokenSecret, time.Duration(constants.ExpiresInSeconds)*time.Second)
}
func CheckValidToken(r *http.Request, tokenSecret string) (uuid.UUID, error) {
	token, err := auth.GetBearerToken(r.Header)
	if err != nil {
		//RespondWithError(w, http.StatusUnauthorized, err.Error())
		return uuid.Nil, err
	}
	userId, err := auth.ValidateJWT(token, tokenSecret)
	if err != nil {
		return uuid.Nil, err
	}
	return userId, nil
}
