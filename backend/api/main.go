package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/constants"
	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/internal/database"
	"github.com/PTIT-Assignment-Projects/vietnamese-news-retrieval-system/backend/api/routing"
	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

func MiddlewareCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "http://localhost:5173")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		w.Header().Set("Access-Control-Allow-Credentials", "true")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func main() {
	_ = godotenv.Load()
	dbURL := os.Getenv(constants.DbUrl)
	db, err := sql.Open(constants.DriverName, dbURL)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	dbQueries := database.New(db)

	mux := http.NewServeMux()
	fileServer := http.FileServer(http.Dir("."))

	apiConfig := &routing.ApiConfig{
		Queries:   dbQueries,
		Db:        db,
		JwtSecret: os.Getenv(constants.JwtSecret),
	}
	appHandler := apiConfig.HandleFile(http.StripPrefix("/app/", fileServer))
	mux.Handle("/app/", appHandler)
	//Health check
	mux.HandleFunc(fmt.Sprintf("%s /api/v1/health", constants.GetMethod), routing.HealthCheckHandler)
	//AUTH
	mux.HandleFunc(fmt.Sprintf("%s /api/v1/auth/register", constants.PostMethod), apiConfig.HandleRegister)
	mux.HandleFunc(fmt.Sprintf("%s /api/v1/auth/login", constants.PostMethod), apiConfig.HandleLogin)
	mux.HandleFunc(fmt.Sprintf("%s /api/v1/auth/refresh", constants.PostMethod), apiConfig.HandleCreateTokenByRefreshToken)
	mux.HandleFunc(fmt.Sprintf("%s /api/v1/auth/logout", constants.PostMethod), apiConfig.HandleRevokeRefreshToken)
	mux.HandleFunc(fmt.Sprintf("%s /api/v1/auth/account", constants.GetMethod), apiConfig.HandleFetchAccount)

	server := &http.Server{
		Addr:    ":8080",
		Handler: MiddlewareCORS(mux),
	}
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		fmt.Errorf("server error : %v", err)
	}
}
