# Vietnamese news retrieval system API service

## Goose migration

**Install**: 
```bash
go install github.com/pressly/goose/v3/cmd/goose@latest
```
**Migrate**: 
```bash
goose postgres "" up
```

## SQLC type-safe query generate
**Install**:
go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest

**Create sqlc.yml file**

**Generate**:
```bash
sqlc generate
```