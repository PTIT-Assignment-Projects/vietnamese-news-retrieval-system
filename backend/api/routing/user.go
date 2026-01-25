package routing

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/auth"
	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/constants"
	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/database"
)

// STRUCT

// createUserRequest create user(register)
type createUserRequest struct {
	Email    string `json:"email"`
	Name     string `json:"name"`
	Password string `json:"password"`
}
type CreateUserResponse struct {
	ID        string    `json:"id"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	Name      string    `json:"name"`
	Email     string    `json:"email"`
}

// HANDLER

func (config *ApiConfig) HandleRegister(w http.ResponseWriter, r *http.Request) {
	var request createUserRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		ResponseWithError(w, http.StatusBadRequest, constants.InvalidRequestBody)
		return
	}
	if !checkEmptyString(request.Email, constants.EmailRequired, w) {
		return
	}
	if !checkEmptyString(request.Name, constants.UserNameRequired, w) {
		return
	}
	password, err := auth.HashPassword(request.Password)
	if err != nil {
		ResponseWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	params := database.CreateUserParams{
		Name:     request.Name,
		Email:    request.Email,
		Password: password,
	}
	user, err := config.Queries.CreateUser(r.Context(), params)
	if err != nil {
		ResponseWithError(w, http.StatusInternalServerError, constants.FailedToCreateUser)
		return
	}
	ResponseWithJSON(w, http.StatusCreated, mapToCreateUserResponse(user))
}

// HELPER METHODS
func checkEmptyString(s, errorMessage string, w http.ResponseWriter) bool {
	if s == "" {
		ResponseWithError(w, http.StatusBadRequest, errorMessage)
		return false
	}
	return true
}

// MAPPER
func mapToCreateUserResponse(user database.CreateUserRow) CreateUserResponse {
	return CreateUserResponse{
		ID:        user.ID.String(),
		CreatedAt: user.CreatedAt,
		UpdatedAt: user.UpdatedAt,
		Name:      user.Name,
		Email:     user.Email,
	}
}
