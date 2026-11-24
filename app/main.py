
import time

from fastapi import FastAPI, Request
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from .database import criar_tabelas
from .routes.registros import router as registros_router

app = FastAPI(
    title="API de Gerenciamento",
    description="API com observabilidade usando Prometheus e Grafana.",
    version="4.0.0"
)


@app.on_event("startup")
def startup_event():
    criar_tabelas()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    inicio = time.time()

    try:
        response = await call_next(request)
        duracao = time.time() - inicio

        logger.info(
            "{} {} - Status: {} - Tempo: {:.4f}s",
            request.method,
            request.url.path,
            response.status_code,
            duracao
        )

        return response

    except Exception:
        logger.exception(
            "Erro ao processar {} {}",
            request.method,
            request.url.path
        )
        raise


app.include_router(registros_router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
