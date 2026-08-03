# Triumf Background Remover

Веб-приложение для удаления фона изображений. Backend построен на FastAPI, frontend отдается как статические файлы. Результат возвращается в PNG с прозрачным alpha-каналом.

## Что реализовано

- исследование методов и SOTA: [docs/research.md](docs/research.md);
- архитектура и API: [docs/architecture.md](docs/architecture.md);
- REST API `POST /api/remove-background`;
- responsive UI с drag & drop, preview, индикатором обработки и скачиванием результата;
- clean backend structure: API, domain, services, infrastructure;
- `.env` конфигурация, JSON-логирование, validation и exception handling.

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --host 127.0.0.1 --port 8000
```

Откройте http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs

При первом запуске `rembg` скачает веса модели в локальный cache. Это может занять время.

## API

```bash
curl -X POST http://127.0.0.1:8000/api/remove-background ^
  -F "image=@input.jpg" ^
  --output result.png
```

Поддерживаемые форматы входа: JPEG, PNG, WEBP.

Выход: PNG с прозрачностью.

## Конфигурация

Скопируйте `.env.example` в `.env`.

| Переменная | Назначение |
| --- | --- |
| `APP_HOST` / `APP_PORT` | host и port приложения |
| `LOG_LEVEL` | уровень логирования |
| `MAX_IMAGE_SIZE_MB` | лимит размера файла |
| `MAX_IMAGE_PIXELS` | лимит количества пикселей |
| `ALLOWED_ORIGINS` | CORS allowlist |
| `REMBG_MODEL` | модель rembg, по умолчанию `bria-rmbg` |

## Выбор модели

| Тип изображения | Модель в UI |
| --- | --- |
| Фото, товары, mixed | **Универсальный (рекомендуется)** — `bria-rmbg` |
| Иллюстрации, аниме, стикеры | **Иллюстрации и аниме** — `isnet-anime` |
| Сложные границы | **Максимальная детализация** — `birefnet-general-lite` |
| Быстрый preview | **Быстрый режим** — `u2net` |

Подробное исследование и обоснование SOTA: [docs/research.md](docs/research.md).

## Выбор модели (технически)

В проекте по умолчанию используется `rembg` + `bria-rmbg`: это наиболее практичный баланс качества для mixed uploads на CPU. Для иллюстраций и аниме выбирайте `isnet-anime`. BiRefNet даёт более сильные результаты на сложных границах, но требует большего compute budget. Подробное сравнение находится в [docs/research.md](docs/research.md).

## Структура

```text
app/
  api/
  core/
  domain/
  infrastructure/
  services/
frontend/
docs/
tests/
main.py
requirements.txt
```

## Проверка

```bash
python -m compileall app main.py
pytest
```

## Production notes

- Запускайте за reverse proxy с TLS.
- Ограничьте CORS конкретным frontend-доменом.
- Для CPU inference начинайте с 1 worker, чтобы не дублировать память модели.
- Для высокой нагрузки вынесите inference в отдельный сервис или очередь задач.
- Настройте лимиты upload на reverse proxy на тот же размер, что и `MAX_IMAGE_SIZE_MB`.

