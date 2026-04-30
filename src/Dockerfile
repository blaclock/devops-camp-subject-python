FROM python:3.12-slim AS builder

WORKDIR /app

# 本番用依存だけを venv に入れる（最終イメージへコピーする成果物を明確化）
ENV VENV_PATH=/opt/venv
RUN python -m venv "$VENV_PATH"
ENV PATH="$VENV_PATH/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS runtime

RUN useradd -m -u 10000 appuser

WORKDIR /app/src

ENV VENV_PATH=/opt/venv
ENV PATH="$VENV_PATH/bin:$PATH"

ENV PYTHONPATH=/app/src

COPY --from=builder "$VENV_PATH" "$VENV_PATH"
COPY . .

RUN chown -R appuser:appuser /app /opt/venv

EXPOSE 8000

USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
