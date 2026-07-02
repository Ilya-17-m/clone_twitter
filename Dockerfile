FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry=="2.3.3"

RUN poetry config virtualenvs.create false --local

COPY pyproject.toml poetry.lock README.md ./

RUN poetry install --no-root

COPY . .
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "backend.clone_twitter:app", "--host", "127.0.0.1", "--port", "8000"]
