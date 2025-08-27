# syntax=docker/dockerfile:1
# Multi-stage build para otimizar imagem final

FROM python:3.11-slim AS builder

# Argumentos de build para tracking
ARG GIT_COMMIT_SHA=unknown
ARG BUILD_DATE=unknown

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências Python
COPY requirements_base.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir -r requirements_base.txt -w /wheels

FROM python:3.11-slim

# Argumentos de build
ARG GIT_COMMIT_SHA=unknown
ARG BUILD_DATE=unknown

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GIT_COMMIT_SHA=${GIT_COMMIT_SHA} \
    BUILD_DATE=${BUILD_DATE} \
    CONTAINER_START_TIME=""

# Labels para metadados da imagem
LABEL maintainer="Necessito Team <suporteindicaai@hotmail.com>" \
      version="1.0.0" \
      description="Necessito - Marketplace B2B/B2C" \
      git.commit="${GIT_COMMIT_SHA}" \
      build.date="${BUILD_DATE}"

# Instalar dependências mínimas de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar wheels do stage builder e instalar
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copiar código da aplicação
COPY . .

# Criar usuário não-root
RUN useradd -m appuser && \
    mkdir -p /app/logs /app/staticfiles /app/media && \
    mkdir -p /app/media/fotos_usuarios /app/media/anuncios /app/media/categorias && \
    chown -R appuser:appuser /app

# Verificação de saúde da imagem
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

USER appuser

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD echo "Container started at: $(date -Iseconds)" > /tmp/container_start && \
    export CONTAINER_START_TIME=$(cat /tmp/container_start) && \
    exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 30