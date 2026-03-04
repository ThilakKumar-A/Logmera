<div align="center">

# 🔭 Logmera

**Self-hosted AI observability. Your data, your infrastructure, your rules.**
</div>

## What is Logmera?

Logmera is a **self-hosted LLM monitoring and observability platform** for developers building AI-powered applications.

Instead of sending your AI data to a third-party cloud, Logmera runs on your own infrastructure and stores everything in your own PostgreSQL database. You get a full observability stack — prompt logging, response tracking, latency analysis, and a built-in dashboard — with complete data privacy.

**Built for teams shipping:**
- AI SaaS applications
- Chatbots and voice agents
- LLM pipelines and RAG systems
- Multi-agent workflows
- AI automation products

---

## Why Logmera?

| | Logmera | Cloud Observability Tools |
|---|---|---|
| **Data location** | Your infrastructure | Vendor's cloud |
| **Privacy** | ✅ Full control | ❌ Data leaves your stack |
| **Vendor lock-in** | ✅ None | ❌ Subscription dependency |
| **Setup time** | ~2 minutes | Account + integration setup |
| **Cost** | Infrastructure only | Per-seat / per-event pricing |
| **Customizable** | ✅ Open source | ❌ Limited |

---

## ✨ Features

- **Prompt & response logging** — capture every input/output with metadata
- **Latency tracking** — measure real-world model response times
- **Built-in web dashboard** — search, filter, and analyze logs visually
- **REST API** — integrate with any language or framework
- **Python SDK** — one-line logging from your AI app
- **PostgreSQL storage** — structured, indexed, queryable logs
- **FastAPI backend** — fast, async, production-ready
- **Simple CLI startup** — running in seconds with a single command
- **Self-hosted** — deploy anywhere: local, Docker, VPS, Kubernetes

---

## 🏗️ Architecture

```
Your AI Application
        │
        ▼
  Logmera Python SDK  ──or──  REST API (any language)
        │
        ▼
  Logmera Backend (FastAPI)
        │
        ▼
  PostgreSQL Database
        │
        ▼
  Web Dashboard (built-in)
```

Logmera is intentionally simple. Your app sends logs to the backend. The backend stores them in PostgreSQL. The dashboard reads from PostgreSQL. No message queues, no external dependencies, no surprises.

---

## ⚡ Quick Start

Get Logmera running in under 2 minutes.

### 1. Install

```bash
pip install logmera
```

### 2. Set up PostgreSQL

Choose the option that fits your setup:

**Option A — Use an existing PostgreSQL database (recommended)**

If you already have PostgreSQL running locally or in the cloud (Supabase, Neon, AWS RDS, etc.), point Logmera at it:

```bash
logmera --db-url "postgresql://username:password@localhost:5432/mydb"
```

Logmera will create its tables automatically. No manual schema setup required.

**Option B — Spin up PostgreSQL with Docker**

```bash
docker run --name logmera-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=logmera \
  -p 5432:5432 -d postgres:16
```

Then start Logmera:

```bash
logmera --db-url "postgresql://postgres:postgres@localhost:5432/logmera"
```

### 3. Start the server

```bash
logmera --db-url "postgresql://postgres:postgres@localhost:5432/logmera"
```

The server starts at `http://127.0.0.1:8000` by default.

To customize the host and port:

```bash
logmera --host 0.0.0.0 --port 8080 --db-url "postgresql://postgres:postgres@localhost:5432/logmera"
```

### 4. Open the dashboard

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser — your dashboard is ready.

---

## 📊 Dashboard

The Logmera dashboard gives you full visibility into your AI application:

- **Browse logs** — view every prompt/response pair in reverse chronological order
- **Search prompts** — find specific inputs fast
- **Filter by project, model, or status** — drill into specific subsets
- **Analyze latency** — identify slow calls and performance regressions
- **Monitor failures** — surface errors and unexpected model behavior

---

## 🐍 Python SDK

### Basic logging

```python
import logmera

logmera.log(
    project_id="my-chatbot",
    prompt="What is the capital of France?",
    response="The capital of France is Paris.",
    model="gpt-4o",
    latency_ms=213,
    status="success"
)
```

### Logging errors

```python
logmera.log(
    project_id="my-chatbot",
    prompt="Summarize this document",
    response=None,
    model="gpt-4o",
    latency_ms=5012,
    status="error"
)
```

---

## 🌐 REST API

Logmera exposes a simple REST API, so you can send logs from any language.

### Health check

```bash
curl http://127.0.0.1:8000/health
# → {"status": "ok"}
```

### Create a log

```bash
curl -X POST http://127.0.0.1:8000/logs \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-app",
    "prompt": "Translate hello to Spanish",
    "response": "Hola",
    "model": "gpt-4o-mini",
    "latency_ms": 95,
    "status": "success"
  }'
```

### Get logs

```bash
curl http://127.0.0.1:8000/logs
```

Returns all logs ordered newest-first.

### Endpoints summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/logs` | Create a new log entry |
| `GET` | `/logs` | Retrieve all logs (newest first) |

---

## ⚙️ Configuration

### CLI flags

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Server bind address |
| `--port` | `8000` | Server port |
| `--db-url` | *(required)* | PostgreSQL connection string |

### Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `DB_POOL_SIZE` | Connection pool size |
| `DB_MAX_OVERFLOW` | Max overflow connections |
| `LOGMERA_URL` | SDK target server URL |
| `LOGMERA_TIMEOUT_SECONDS` | SDK request timeout |
| `LOGMERA_RETRIES` | SDK retry attempts on failure |

---

## 🗄️ Database Schema

Each log entry in PostgreSQL includes:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Unique log identifier |
| `project_id` | TEXT | Your application or project name |
| `prompt` | TEXT | The input sent to the model |
| `response` | TEXT | The model's output |
| `model` | TEXT | Model name (e.g. `gpt-4o`) |
| `latency_ms` | INTEGER | Response time in milliseconds (Optional) |
| `status` | TEXT | `success`, `error`, etc. (Optional)|
| `timestamp` | TIMESTAMP | When the log was created |

Indexes are applied on `project_id` and `timestamp` for fast querying at scale.

---

## 🚀 Production Deployment

Logmera is designed to run wherever your infrastructure lives.

### Docker

```dockerfile
FROM python:3.11-slim
RUN pip install logmera
CMD ["logmera", "--host", "0.0.0.0", "--port", "8000", "--db-url", "postgresql://user:pass@db:5432/logmera"]
```

### Docker Compose

```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: logmera
    volumes:
      - pgdata:/var/lib/postgresql/data

  logmera:
    image: python:3.11-slim
    command: >
      sh -c "pip install logmera &&
             logmera --host 0.0.0.0 --port 8000
             --db-url postgresql://postgres:postgres@db:5432/logmera"
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  pgdata:
```

### Supported deployment targets

- Local machines (development)
- Docker containers
- VPS / bare metal servers
- Kubernetes clusters
- Cloud VMs (AWS EC2, GCP Compute, Azure VM)

Since Logmera is fully self-hosted, **your AI logs never leave your infrastructure**.

---

## 📦 Use Cases

**Debugging prompts** — see exactly what was sent to the model and what came back, with timing.

**Monitoring AI agents** — log every step of a multi-agent pipeline and trace failures.

**Tracking RAG pipelines** — observe retrieval inputs and generation outputs together.

**Latency analysis** — identify which models or prompt patterns are slowest in production.

**Error monitoring** — surface failed LLM calls and build alerting around them.

**Compliance & auditing** — keep a complete, private record of all AI interactions.

---

## 🤝 Contributing

Contributions are welcome! Whether it's a bug fix, a new feature, or improved documentation, feel free to open an issue or submit a pull request.

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feat/my-feature`)
5. Open a Pull Request

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and self-host.

---


<div align="center">

**[PyPI](https://pypi.org/project/logmera/) · [GitHub](https://github.com/ThilakKumar-A/Logmera/) · [Report a Bug](https://github.com/ThilakKumar-A/Logmera/issues)**

Built for developers who want observability without the black box.

</div>
