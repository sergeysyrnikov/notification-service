# notification-service

Мини-сервис уведомлений на Python (FastAPI).

## Что умеет

- Принимать события через HTTP `POST /api/v1/events` и валидировать payload в зависимости от `type`
- Рассылать состояние job подписчикам через WebSocket `WS /ws`
- Хранить состояние в памяти (in-memory) внутри процесса FastAPI

## Требования

- Python >= 3.12
- Docker (опционально, для контейнеризации)

## Локальный запуск

1. Установите зависимости:
```bash
uv sync
```

2. Запустите сервер:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер будет доступен по адресу `http://localhost:8000`.

## Запуск тестов

```bash
uv run pytest
```

## Docker

1. Сборка контейнера:
```bash
docker build -t notification-service .
```

2. Запуск контейнера:
```bash
docker run --rm -p 8000:8000 notification-service
```

Примечание: порт внутри контейнера управляется переменной окружения `PORT` (по умолчанию `8000`).

## HTTP API

### `POST /api/v1/events`

Принимает событие и передает его в обработчик сервиса.

Ответ (успех):

```json
{ "ok": true }
```

Статусы:
- `200` — событие успешно обработано
- `422` — ошибка валидации схемы или payload

Поля запроса:
- `type`: один из `job.started`, `job.progress`, `job.finished`
- `product`: строка
- `job_id`: строка
- `timestamp`: ISO 8601 datetime (например, `2026-03-13T10:00:00Z`)
- `payload`: объект, структура зависит от `type`
- Варианты `payload`:
- `job.started`: `{ "status": "<string>" }`
- `job.progress`: `{ "progress": <int 0..100>, "status": "<string>" }`
- `job.finished`: `{ "status": "<string>", "download_url": "<string|null>" }`

Примеры `curl`:

#### `job.started`
```bash
curl -X POST 'http://localhost:8000/api/v1/events' \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "job.started",
    "product": "import",
    "job_id": "123",
    "timestamp": "2026-03-13T10:00:00Z",
    "payload": { "status": "started" }
  }'
```

#### `job.progress`
```bash
curl -X POST 'http://localhost:8000/api/v1/events' \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "job.progress",
    "product": "import",
    "job_id": "123",
    "timestamp": "2026-03-13T10:00:00Z",
    "payload": { "progress": 42, "status": "running" }
  }'
```

#### `job.finished` (success)
```bash
curl -X POST 'http://localhost:8000/api/v1/events' \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "job.finished",
    "product": "import",
    "job_id": "123",
    "timestamp": "2026-03-13T10:00:00Z",
    "payload": {
      "status": "success",
      "download_url": "https://example.com/file.csv"
    }
  }'
```

## WebSocket

### `WS /ws`

Клиент подключается к `ws://localhost:8000/ws` и отправляет JSON:

```json
{ "action": "subscribe", "job_id": "123" }
```

После подписки сервер отправляет текущее состояние (если оно есть) и дальше рассылает обновления для этого `job_id`.

Формат broadcast-сообщения:

```json
{
  "job": {
    "job_id": "123",
    "product": "import",
    "status": "running",
    "progress": 42,
    "updated_at": "2026-03-13T10:00:00Z",
    "download_url": null
  },
  "event_type": "job.progress"
}
```
