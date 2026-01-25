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
	mux.HandleFunc("GET /api/health", routing.HealthCheckHandler)

	server := &http.Server{
		Addr:    ":8080",
		Handler: mux,
	}
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		fmt.Errorf("server error : %v", err)
	}
}
