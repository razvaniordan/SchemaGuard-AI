# Story 1.3 - Spring Boot API Framework Starter

This starter project implements the Story 1.3 criteria for a Java Spring Boot backend:

- OpenAPI/Swagger documentation
- Basic REST routing structure
- Authentication middleware using a demo bearer token
- DTO-based request/response models
- Global exception handling
- Request validation
- Basic endpoint tests

## Requirements

- Java 21
- Maven 3.9+

## Run

```bash
mvn spring-boot:run
```

The API runs on:

```text
http://localhost:8080
```

## Swagger UI

```text
http://localhost:8080/swagger-ui.html
```

OpenAPI JSON:

```text
http://localhost:8080/v3/api-docs
```

## Demo endpoints

### Public health check

```http
GET /api/health
```

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "demo",
  "password": "password"
}
```

Response includes a bearer token.

### Protected endpoints

Use the login response token as:

```http
Authorization: Bearer <token>
```

Available protected endpoints:

```http
GET /api/transactions
POST /api/transactions
```

Example create transaction request:

```json
{
  "merchantName": "Demo Merchant",
  "mcc": "5411",
  "amount": 25.50,
  "currency": "USD"
}
```

## Run tests

```bash
mvn test
```

## Notes

The authentication implementation is intentionally lightweight for starter purposes. Replace the demo token service with a production JWT implementation and database-backed users when moving beyond Story 1.3.
