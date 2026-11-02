# Secure Local LLM API

A containerized REST API for interacting with locally hosted Large Language Models (LLMs) through Ollama, built with FastAPI.

The project provides API key authentication, request validation, rate limiting, error handling, and Docker-based deployment.

## Project Overview

Secure Local LLM API provides a protected interface between client applications and locally hosted language models.

Instead of exposing Ollama directly, clients communicate with a FastAPI service that validates requests, authenticates users, enforces rate limits, and forwards prompts to Ollama.

**Base Model:** Qwen 2.5 0.5B Instruct (via Ollama)

## Architecture

```text
Client Application
       |
       v
FastAPI REST API
       |
       +---- API Key Authentication
       |
       +---- Request Validation
       |
       +---- Rate Limiting
       |
       v
Ollama Local Server
       |
       v
Qwen 2.5 0.5B
       |
       v
Generated Response
```

## Features

- FastAPI REST API.
- Local LLM integration through Ollama.
- API Key authentication using `X-API-Key`.
- Constant-time API key comparison.
- Rate limiting: 5 requests per minute per client IP.
- Input validation using Pydantic.
- Maximum question length: 2,000 characters.
- Request timeout handling.
- Structured HTTP error responses.
- Docker containerization.
- Docker Compose deployment.
- Automated API testing using Pytest and Mock.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API framework |
| Pydantic | Request validation |
| Ollama | Local model serving |
| Qwen 2.5 0.5B | Language model |
| Requests | HTTP communication |
| SlowAPI | Rate limiting |
| Pytest | Automated testing |
| Docker | Containerization |
| Docker Compose | Container management |

## Project Structure

```text
Secure-Local-LLM-API/
│
├── tests/
│   └── test_api.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── logging_config.py
├── main.py
├── main_before_docker.py
├── requirements.txt
├── 03_FastAPI_Local_LLM.ipynb
└── README.md
```

## Requirements

- Python 3.11+
- Docker Desktop
- Docker Compose
- Ollama
- Qwen 2.5 0.5B model

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ahmad-Alqudah/Secure-Local-LLM-API.git

cd Secure-Local-LLM-API
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

PowerShell:

```powershell
$env:API_KEY = "your-secure-api-key"

$env:OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

$env:MODEL_NAME = "qwen2.5:0.5b"
```

### 4. Start Ollama

Make sure Ollama is running and the model is available:

```bash
ollama pull qwen2.5:0.5b
```

### 5. Start FastAPI

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Docker Deployment

### 1. Configure API Key

PowerShell:

```powershell
$env:API_KEY = "your-secure-api-key"
```

### 2. Build and start the application

```bash
docker compose up -d --build
```

### 3. Check container status

```bash
docker compose ps
```

### 4. View application logs

```bash
docker compose logs -f
```

### 5. Stop the application

```bash
docker compose down
```

**Important:** Ollama runs outside the API container. Docker communicates with the Windows host through `host.docker.internal`.

The default exposed API port is `8005`.

## API Endpoints

### 1. Health Check

**GET** `/health`

Example response:

```json
{
  "status": "healthy",
  "service": "Secure Local LLM API"
}
```

### 2. Chat

**POST** `/chat`

Required header:

```text
X-API-Key: your-api-key
```

Request:

```json
{
  "question": "What is Artificial Intelligence?"
}
```

Successful response:

```json
{
  "model": "qwen2.5:0.5b",
  "question": "What is Artificial Intelligence?",
  "answer": "Artificial Intelligence is...",
  "success": true
}
```

## Security and Error Handling

| HTTP Status | Description |
|---|---|
| 200 | Successful response |
| 401 | Missing or invalid API key |
| 422 | Invalid request data |
| 429 | Rate limit exceeded |
| 502 | Invalid or failed LLM response |
| 503 | Ollama server unavailable |
| 504 | LLM request timeout |

Additional security measures:

- API keys are provided through environment variables.
- API key comparison uses `hmac.compare_digest`.
- Passwords and API keys should never be committed to GitHub.
- Request size is constrained through Pydantic validation.

## Automated Testing

The project includes automated tests using Pytest and mocked Ollama responses.

Run tests:

```bash
python -m pytest tests/test_api.py -v
```

**Test Results: 9/9 Passed**

Test coverage includes:

- Health endpoint.
- Missing API key.
- Invalid API key.
- Empty question validation.
- Maximum question length validation.
- Successful chat response.
- Ollama connection errors.
- Ollama timeout handling.
- Invalid Ollama responses.

The real Ollama integration was also tested separately through the running Docker container.

## Limitations

- Uses a locally hosted model through Ollama.
- Model performance depends on available hardware.
- Rate limiting currently uses the application's configured SlowAPI limiter.
- Health endpoint checks API availability, not Ollama model availability.
- The current authentication implementation uses a shared API key.
- This project has not undergone a full production security audit.

## Future Improvements

- Add persistent API key management.
- Integrate structured request logging and latency tracking.
- Add monitoring and observability.
- Implement stronger authentication and authorization.
- Add automated integration tests against a controlled Ollama instance.
- Add production deployment configuration.

## Author

**Ahmad Alqudah**

AI Engineer | Machine Learning | Deep Learning | LLMs | RAG | AI Agents

GitHub: https://github.com/Ahmad-Alqudah

---

*Developed as part of practical AI and LLM engineering projects.*
