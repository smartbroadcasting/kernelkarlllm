# API

## GET /health

```json
{
  "status": "ok"
}
```

## GET /models

```json
{
  "backend": "llama.cpp",
  "loaded": false,
  "model_path": "/models/qwen3-14b-instruct-q4_k_m.gguf",
  "loaded_model": null,
  "context": 8192,
  "threads": 8,
  "gpu_layers": 0
}
```

## POST /generate

```json
{
  "prompt": "Fasse diesen Text zusammen",
  "temperature": 0.2,
  "max_tokens": 800
}
```

Response:

```json
{
  "text": "..."
}
```

## POST /chat

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Du bist Kernel Karl."
    },
    {
      "role": "user",
      "content": "Hallo"
    }
  ],
  "temperature": 0.2
}
```

Response:

```json
{
  "message": {
    "role": "assistant",
    "content": "..."
  }
}
```

## POST /embed

```json
{
  "text": "..."
}
```

Response:

```json
{
  "embedding": []
}
```

## Errors

```json
{
  "error": true,
  "message": "Model not found: /models/qwen3-14b-instruct-q4_k_m.gguf"
}
```
