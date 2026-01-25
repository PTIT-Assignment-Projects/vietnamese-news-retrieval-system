package auth

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/constants"
)

func MakeRefreshToken() (string, error) {
	b := make([]byte, 32)
	n, err := rand.Read(b)
	if err != nil {
		return "", err
	}
	if n != len(b) {
		return "", fmt.Errorf(constants.ShortReadFromCryptoRand)
	}
	return hex.EncodeToString(b), nil
}
