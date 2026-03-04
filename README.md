<div align="center">

# 🔭 Logmera

**Self-hosted monitoring for AI applications**

Log prompts, responses, and latency from your AI apps and view them in a simple dashboard.

</div>

---
Source Code: https://github.com/ThilakKumar-A/Logmera/
--
## What is Logmera?

Logmera is a **self-hosted observability tool for AI / LLM applications**.

It helps developers understand what their AI systems are doing.

Instead of printing logs to the console, Logmera stores:

* prompts
* responses
* model name
* latency

in a **PostgreSQL database** and shows them in a **web dashboard**.

Your data stays on **your infrastructure**.

---

## Dashboard

![Dashboard](dashboard.png)

---

## Why use Logmera?

When building AI applications it becomes hard to know:

* what prompts were sent
* what responses were returned
* how long requests took
* which model was used
* when errors happened

Logmera helps you **see and monitor all AI activity in one place**.

---

## How it works

```
Your AI App
     │
     ▼
Logmera SDK
     │
     ▼
Logmera Server
     │
     ▼
PostgreSQL
     │
     ▼
Dashboard
```

Your application sends logs to Logmera.
Logmera stores them and displays them in the dashboard.

---

## Quick Start

### 1. Install

```bash
pip install logmera
```

---

### 2. Start PostgreSQL

You can use any PostgreSQL database.

Example connection string:

```
postgresql://username:password@localhost:5432/database
```

If you do not have PostgreSQL installed, you can run it with Docker.

```bash
docker run --name logmera-postgres \
-e POSTGRES_USER=postgres \
-e POSTGRES_PASSWORD=postgres \
-e POSTGRES_DB=logmera \
-p 5432:5432 -d postgres:16
```

---

### 3. Start Logmera

```bash
logmera --db-url "postgresql://postgres:postgres@localhost:5432/logmera"
```

Server starts at:

```
http://127.0.0.1:8000
```

---

## Open the Dashboard

Open your browser:

```
http://127.0.0.1:8000
```

You will see your AI logs in the dashboard.

---

## Python Example

Add Logmera to your AI code.

```python
import logmera

logmera.log(
    project_id="chatbot",
    prompt="Hello",
    response="Hi there",
    model="gpt-4o",
    latency_ms=120,
    status="success"
)
```

Now the request will appear in the Logmera dashboard.

---

## API Example

You can also send logs using the API.

```bash
curl -X POST http://127.0.0.1:8000/logs \
-H "Content-Type: application/json" \
-d '{
  "project_id":"my-app",
  "prompt":"Hello",
  "response":"Hi",
  "model":"gpt-4o",
  "latency_ms":95,
  "status":"success"
}'
```

---

## API Endpoints

| Method | Endpoint  | Description  |
| ------ | --------- | ------------ |
| GET    | `/health` | Health check |
| POST   | `/logs`   | Create log   |
| GET    | `/logs`   | Get logs     |

---

## Configuration

Example CLI:

```
logmera --host 127.0.0.1 --port 8000
```

Environment variables:

```
DATABASE_URL
LOGMERA_URL
LOGMERA_TIMEOUT_SECONDS
LOGMERA_RETRIES
```

---

## Deployment

Logmera can run on:

* Local machines
* Docker
* VPS servers
* Kubernetes
* Cloud VMs

Because Logmera is **self-hosted**, your AI data remains private.

---

## License

MIT License

---

## Links

<div align="center">

**[PyPI](https://pypi.org/project/logmera/) · [GitHub](https://github.com/ThilakKumar-A/Logmera/) · [Report a Bug](https://github.com/ThilakKumar-A/Logmera/issues)**

Built for developers who want observability without the black box.

</div>
