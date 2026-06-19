# Kernel Karl LLM

Lokaler LLM-Microservice fuer Kernel Karl. Der Dienst stellt eine stabile REST-API bereit und kapselt die konkrete LLM-Engine vollstaendig vom aufrufenden PHP-System.

Kernel Karl kommuniziert ausschliesslich per HTTP mit diesem Service. Modell- und Backendwechsel erfolgen innerhalb von `kernel-karl-llm`, nicht im PHP-Code.

## Architektur

```text
Kernel Karl (PHP)
        |
        | HTTP REST
        v
kernel-karl-llm
        |
        +-- FastAPI
        |
        +-- Backend Adapter
                |
                +-- llama.cpp (Phase 1)
                +-- vLLM / OpenAI / Azure OpenAI (spaeter)
```

## Features

- Python 3.11
- FastAPI + Uvicorn
- llama-cpp-python als Phase-1-Backend
- GGUF-Modellformat
- CPU-first Betrieb mit `MODEL_GPU_LAYERS=0`
- GPU-Migration vorbereitet ueber Konfiguration
- strukturierte JSON-Logs
- einheitliche JSON-Fehlerantworten
- Backend-Adapter fuer spaetere vLLM-, OpenAI- oder Cluster-Backends
- MCP-Verzeichnisstruktur fuer spaetere Integrationen

## Struktur

```text
kernel-karl-llm/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── app.py
├── config/
│   └── settings.py
├── api/
│   ├── chat.py
│   ├── generate.py
│   ├── embeddings.py
│   ├── health.py
│   └── models.py
├── services/
│   ├── backend_adapter.py
│   ├── llm_service.py
│   └── model_loader.py
├── models/
├── mcp/
├── docs/
└── README.md
```

## Standardmodell

Phase 1 ist fuer folgendes GGUF-Modell vorbereitet:

```text
Qwen3-14B-Instruct-Q4_K_M.gguf
```

Das Modell wird nicht im Git-Repository gespeichert. Lege die Datei lokal in `models/` ab.

Beispiel:

```bash
mkdir -p models
cp Qwen3-14B-Instruct-Q4_K_M.gguf models/qwen3-14b-instruct-q4_k_m.gguf
```

Der Standardpfad im Container lautet:

```env
MODEL_PATH=/models/qwen3-14b-instruct-q4_k_m.gguf
```

## Installation Auf Einem Neuen Server

Voraussetzungen:

- Ubuntu Server oder vergleichbares Linux
- Docker Engine
- Docker Compose Plugin
- Zugriff auf das GitHub-Repository
- GGUF-Modellfile, zum Beispiel `Qwen3-14B-Instruct-Q4_K_M.gguf`

### 1. Docker Pruefen

```bash
docker --version
docker compose version
```

Falls Docker Compose nicht als Plugin installiert ist, kann auf aelteren Systemen der Befehl `docker-compose` statt `docker compose` noetig sein.

### 2. Projekt Klonen

Per SSH:

```bash
cd /opt
git clone git@github.com:smartbroadcasting/kernelkarlllm.git kernel-karl-llm
cd kernel-karl-llm
```

Oder per HTTPS mit GitHub Personal Access Token:

```bash
cd /opt
git clone https://github.com/smartbroadcasting/kernelkarlllm.git kernel-karl-llm
cd kernel-karl-llm
```

GitHub akzeptiert bei HTTPS kein normales Account-Passwort fuer Git-Operationen. Als Passwort muss ein Personal Access Token verwendet werden.

### 3. Konfiguration Anlegen

```bash
cp .env.example .env
```

Standardkonfiguration:

```env
API_PORT=8100
BACKEND=llama_cpp
MODEL_PATH=/models/qwen3-14b-instruct-q4_k_m.gguf
MODEL_CONTEXT=8192
MODEL_THREADS=8
MODEL_GPU_LAYERS=0
LOG_LEVEL=INFO
```

Wichtige Werte:

- `API_PORT`: Port auf dem Host, Standard `8100`
- `MODEL_PATH`: Pfad des GGUF-Modells im Container
- `MODEL_CONTEXT`: Kontextgroesse
- `MODEL_THREADS`: CPU-Threads, `8` als konservativer Default
- `MODEL_GPU_LAYERS`: `0` fuer CPU-Betrieb

### 4. Modell Ablegen

Das Modell wird nicht mit Git ausgeliefert. Lege das GGUF-File in den lokalen Ordner `models/`.

```bash
mkdir -p models
cp /pfad/zum/Qwen3-14B-Instruct-Q4_K_M.gguf models/qwen3-14b-instruct-q4_k_m.gguf
```

Der Dateiname muss zum `MODEL_PATH` in `.env` passen:

```env
MODEL_PATH=/models/qwen3-14b-instruct-q4_k_m.gguf
```

Der lokale Ordner `models/` wird per Docker Compose nach `/models` in den Container gemountet.

## Docker Build

```bash
docker compose build
```

Falls dein System noch die alte Compose-Binary nutzt:

```bash
docker-compose build
```

## Container Starten

```bash
docker compose up -d
```

Mit alter Compose-Binary:

```bash
docker-compose up -d
```

Logs:

```bash
docker compose logs -f kernel-karl-llm
```

Health Check:

```bash
curl http://localhost:8100/health
```

Erwartete Antwort:

```json
{
  "status": "ok"
}
```

Modellstatus pruefen:

```bash
curl http://localhost:8100/models
```

Wenn das Modell noch nicht geladen oder nicht vorhanden ist, liefern Generate/Chat/Embed eine saubere JSON-Fehlermeldung.

## Container Verwaltung

Status:

```bash
docker compose ps
```

Neustart:

```bash
docker compose restart kernel-karl-llm
```

Stoppen:

```bash
docker compose down
```

Neu bauen und starten:

```bash
docker compose build --pull
docker compose up -d
```

## API Beispiele

Modelle:

```bash
curl http://localhost:8100/models
```

Generate:

```bash
curl -X POST http://localhost:8100/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Fasse diesen Text zusammen: Kernel Karl ist ein lokaler KI-Dienst.",
    "temperature": 0.2,
    "max_tokens": 800
  }'
```

Chat:

```bash
curl -X POST http://localhost:8100/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "Du bist Kernel Karl."},
      {"role": "user", "content": "Hallo"}
    ],
    "temperature": 0.2
  }'
```

Embeddings:

```bash
curl -X POST http://localhost:8100/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Kernel Karl analysiert Nachrichten."}'
```

## Fehlerformat

Alle Fehler werden als JSON zurueckgegeben:

```json
{
  "error": true,
  "message": "Model not found: /models/qwen3-14b-instruct-q4_k_m.gguf"
}
```

## Logging

Logs werden als JSON auf stdout geschrieben und sind dadurch direkt in Container-Logs sichtbar.

Beispiel:

```json
{
  "level": "INFO",
  "message": "request_completed",
  "endpoint": "/generate",
  "duration_ms": 234,
  "status_code": 200
}
```

## Update Prozess

```bash
git pull
docker compose build --pull
docker compose up -d
docker compose logs -f kernel-karl-llm
```

## Keine Ollama-Abhaengigkeit

Der Dienst verwendet keine Ollama CLI, keine Ollama API und keine Shell-Aufrufe zu Ollama.

## Roadmap

Phase 2 kann hinter dem bestehenden API-Vertrag ergaenzt werden:

- vLLM Backend
- OpenAI Backend
- Azure OpenAI Backend
- RAG
- Wissensdatenbank
- MCP Server
- Agentenfunktionen
- Tool Calling
