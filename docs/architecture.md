# Architecture

## Technology stack

- Backend: FastAPI, Pydantic Settings, Pillow, rembg, ONNX Runtime, structlog.
- Frontend: HTML, CSS, vanilla JavaScript.
- Runtime model: `bria-rmbg` by default through `rembg`, with selectable alternatives (`isnet-anime`, `isnet-general-use`, `birefnet-general-lite`, `u2net`).
- Output format: PNG with alpha channel.

## Project structure

```text
app/
  api/                 HTTP routes and response schemas
  core/                configuration, logging, exception handlers
  domain/              validation, exceptions, service ports
  infrastructure/      model adapter implementation
  services/            application use cases
frontend/              browser UI served by FastAPI
docs/                  research and architecture notes
tests/                 unit tests
main.py                ASGI entrypoint
```

## Request pipeline

1. Browser uploads an image with `multipart/form-data`.
2. API validates content type, file size and image integrity.
3. Pillow decodes the image; inference input is normalized to RGB via `prepare_for_inference`.
4. Background remover adapter runs model inference (model selected via query param).
5. Result is encoded as optimized PNG.
6. API returns `image/png` with `Content-Disposition` for download.

## REST API

### `GET /api/health`

Returns:

```json
{"status":"ok"}
```

### `GET /api/models`

Returns available rembg models and the configured default.

### `POST /api/remove-background`

Request:

- `Content-Type: multipart/form-data`
- field `image`: JPEG, PNG or WEBP
- query `model`: optional rembg model id (`bria-rmbg`, `isnet-anime`, ...)
- query `alpha_matting`: optional bool, refines hair/translucent edges
- query `post_process_mask`: optional bool, morphological mask smoothing

Responses:

- `200 image/png`: image with transparent background
- `400`: empty/corrupt image
- `413`: file or resolution limit exceeded
- `415`: unsupported media type
- `500`: model or processing failure

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/remove-background \
  -F "image=@input.jpg" \
  --output result.png
```

## Security

- Strict upload type allowlist.
- Server-side decoding validation, not just MIME trust.
- File size and pixel count limits against memory pressure and decompression bombs.
- No uploaded files are persisted.
- CORS is configurable and restricted by default to local origins.
- Errors return concise messages without internal traces.

## Scalability

- The model session is cached per worker process.
- For CPU deployments, use one or a small number of workers to avoid duplicated model memory.
- For GPU deployments, run a dedicated inference service or worker queue.
- Large batch/background workloads should be moved to asynchronous jobs with object storage.
- The `BackgroundRemover` port isolates model implementation from API and UI.

## Error handling and logging

- Domain validation errors map to explicit HTTP statuses.
- Model failures are wrapped as `ImageProcessingError`.
- Logs are JSON via `structlog`, suitable for stdout-based container logging.

