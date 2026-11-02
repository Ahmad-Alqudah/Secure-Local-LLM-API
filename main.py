
# ============================================================
# Local LLM API - Authentication + Rate Limiting
# ============================================================

import os
import hmac
import requests

from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse


# ============================================================
# 1 - Application
# ============================================================

app = FastAPI(
    title="Secure Local LLM API",
    version="1.2.0"
)


# ============================================================
# 2 - Environment Configuration
# ============================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "qwen2.5:0.5b"
)

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError(
        "API_KEY environment variable must be configured."
    )


# ============================================================
# 3 - API Key Authentication
# ============================================================

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def verify_api_key(
    provided_key: str | None = Security(api_key_header)
):

    if not provided_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required"
        )

    if not hmac.compare_digest(provided_key, API_KEY):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return provided_key


# ============================================================
# 4 - Rate Limiting
# ============================================================

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded
):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Try again later."
        }
    )


app.add_middleware(SlowAPIMiddleware)


# ============================================================
# 5 - Request Schema
# ============================================================

class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000
    )


# ============================================================
# 6 - Health Endpoint
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Secure Local LLM API"
    }


# ============================================================
# 7 - Protected Chat Endpoint
# ============================================================

@app.post("/chat")
@limiter.limit("5/minute")
def chat(
    request: Request,
    body: ChatRequest,
    _api_key: str = Security(verify_api_key)
):

    payload = {
        "model": MODEL_NAME,
        "prompt": body.question,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        return {
            "model": MODEL_NAME,
            "question": body.question,
            "answer": result["response"],
            "success": True
        }

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="LLM response timed out"
        )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Ollama server is unavailable"
        )

    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError
    ):
        raise HTTPException(
            status_code=502,
            detail="LLM server returned an invalid or failed response"
        )
