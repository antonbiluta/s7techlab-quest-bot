FROM python:3.13-alpine as builder

RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app

COPY . .

RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.13-alpine

COPY --from=builder /venv /venv

WORKDIR /app

ENV PATH="/venv/bin:$PATH"

COPY . .

CMD ["python", "bot.py"]