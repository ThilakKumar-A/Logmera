import logging
import os
from pathlib import Path
import typer
import uvicorn

app = typer.Typer(help="logmera CLI")
CONFIG_DIR = Path.home() / ".logmera"
CONFIG_FILE = CONFIG_DIR / "config.env"


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    
    # Suppress Chrome DevTools 404 errors
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def _read_saved_db_url() -> str | None:
    if not CONFIG_FILE.exists():
        return None

    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("DATABASE_URL="):
            value = stripped.split("=", 1)[1].strip()
            if value:
                return value.strip("\"'")
    return None


def _save_db_url(database_url: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    existing_content = ""
    if CONFIG_FILE.exists():
        existing_content = CONFIG_FILE.read_text(encoding="utf-8")

    lines = existing_content.splitlines()
    updated_lines = []
    db_url_found = False
    
    for line in lines:
        if line.startswith("DATABASE_URL="):
            updated_lines.append(f"DATABASE_URL={database_url}")
            db_url_found = True
        elif line.startswith("LOGMERA_URL="):
            updated_lines.append(line)  
        else:
            updated_lines.append(line)

    if not db_url_found:
        updated_lines.append(f"DATABASE_URL={database_url}")

    CONFIG_FILE.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _save_host(url: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    existing_content = ""
    if CONFIG_FILE.exists():
        existing_content = CONFIG_FILE.read_text(encoding="utf-8")

    lines = existing_content.splitlines()
    updated_lines = []
    url_found = False
    
    for line in lines:
        if line.startswith("LOGMERA_URL="):
            updated_lines.append(f"LOGMERA_URL={url}")
            url_found = True
        elif line.startswith("DATABASE_URL="):
            updated_lines.append(line)  
        else:
            updated_lines.append(line)

    if not url_found:
        updated_lines.append(f"LOGMERA_URL={url}")

    CONFIG_FILE.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _resolve_db_url(cli_db_url: str | None, no_prompt: bool) -> str:
    db_url = cli_db_url or os.getenv("DATABASE_URL") or _read_saved_db_url()
    if db_url:
        return db_url

    if no_prompt:
        raise typer.BadParameter(
            "DATABASE_URL is required. Pass --db-url or set DATABASE_URL env var."
        )

    entered = typer.prompt(
        "Enter PostgreSQL DATABASE_URL",
        default="postgresql://postgres:postgres@localhost:5432/logmera",
        show_default=True,
    ).strip()
    if not entered:
        raise typer.BadParameter("DATABASE_URL cannot be empty.")
    return entered


@app.command("start")
def start_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    db_url: str | None = typer.Option(
        None,
        "--db-url",
        help="PostgreSQL connection URL. Overrides saved/default value.",
    ),
    no_prompt: bool = typer.Option(
        False,
        "--no-prompt",
        help="Fail instead of prompting when database URL is missing.",
    ),
    save_db: bool = typer.Option(
        True,
        "--save-db/--no-save-db",
        help="Save the resolved DATABASE_URL to ~/.logmera/config.env.",
    ),
) -> None:
    _configure_logging()
    resolved_db_url = _resolve_db_url(db_url, no_prompt=no_prompt)
    os.environ["DATABASE_URL"] = resolved_db_url
    os.environ["LOGMERA_URL"] = f"http://{host}:{port}"
    _save_host(f"http://{host}:{port}")
    if save_db:
        _save_db_url(resolved_db_url)
        logging.getLogger("logmera.cli").info(
            "DATABASE_URL saved to %s", CONFIG_FILE
        )

    uvicorn.run("logmera.main:app", host=host, port=port, reload=reload)

def start() -> None:
    app()


if __name__ == "__main__":
    start()
