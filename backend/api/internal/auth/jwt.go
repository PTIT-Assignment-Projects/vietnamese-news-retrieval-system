package auth

import (
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/constants"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

func CreateJWT(userID uuid.UUID, tokenSecret string, expiresIn time.Duration) (string, error) {
	claims := jwt.RegisteredClaims{
		Subject:   userID.String(),
		IssuedAt:  jwt.NewNumericDate(time.Now()),
		ExpiresAt: jwt.NewNumericDate(time.Now().Add(expiresIn)),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(tokenSecret))
}
func ValidateJWT(tokenString, tokenSecret string) (uuid.UUID, error) {
	token, err := jwt.ParseWithClaims(tokenString, &jwt.RegisteredClaims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf(constants.UnexpectedSigningMethodError)
		}
		return []byte(tokenSecret), nil
	})
	if err != nil {
		return uuid.Nil, err
	}
	if !token.Valid {
		return uuid.Nil, fmt.Errorf(constants.InvalidToken)
	}
	claims, ok := token.Claims.(*jwt.RegisteredClaims)
	if !ok || claims.Subject == "" {
		return uuid.Nil, fmt.Errorf(constants.InvalidTokenClaims)
	}
	uid, err := uuid.Parse(claims.Subject)
	if err != nil {
		return uuid.Nil, err
	}
	return uid, nil
}
func GetBearerToken(headers http.Header) (string, error) {
	bearerToken := headers.Get(constants.AuthorizationHeaderField)
	if bearerToken == "" {
		return "", fmt.Errorf(constants.InvalidHeaderFieldValue)
	}
	s := strings.Split(bearerToken, " ")
	if len(s) != 2 || s[0] != constants.BearerField {
		return "", fmt.Errorf(constants.InvalidHeaderFieldValue)
	}
	return s[1], nil
}
