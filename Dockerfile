FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

# Instala uv direto da imagem oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copia apenas arquivos de dependência para aproveitar cache
COPY pyproject.toml uv.lock ./

# Instala dependências sem instalar o projeto
RUN uv sync --frozen --no-install-project

# Copia o restante do código
COPY . .

# Instala o projeto
RUN uv sync --frozen

CMD ["tail", "-f", "/dev/null"]