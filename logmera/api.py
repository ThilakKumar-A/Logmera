import json
import logging
from collections.abc import Sequence
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from logmera.database import get_db_session, init_db
from logmera.models import LogEntry
from logmera.schemas import HealthResponse, LogCreate, LogRead

logger = logging.getLogger("logmera.api")

router = APIRouter()
DASHBOARD_DIR = Path(__file__).resolve().parent / "dashboard"


@router.get("/")
async def dashboard() -> FileResponse:
    return FileResponse(DASHBOARD_DIR / "index.html")


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/logs", response_model=LogRead, status_code=status.HTTP_201_CREATED)
async def create_log(
    payload: LogCreate,
    db: AsyncSession = Depends(get_db_session),
) -> LogRead:
    record = LogEntry(**payload.model_dump())
    db.add(record)

    try:
        await db.commit()
        await db.refresh(record)
        logger.info(
            json.dumps(
                {
                    "event": "log_created",
                    "log_id": str(record.id),
                    "project_id": record.project_id,
                    "model": record.model,
                }
            )
        )
        return LogRead.model_validate(record)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception(
            json.dumps(
                {
                    "event": "db_write_error",
                    "error": str(exc.__class__.__name__),
                }
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store log",
        ) from exc


@router.get("/logs", response_model=list[LogRead])
async def list_logs(db: AsyncSession = Depends(get_db_session)) -> list[LogRead]:
    stmt = select(LogEntry).order_by(desc(LogEntry.created_at))
    try:
        result = await db.execute(stmt)
        rows: Sequence[LogEntry] = result.scalars().all()
        return [LogRead.model_validate(row) for row in rows]
    except SQLAlchemyError as exc:
        logger.exception(
            json.dumps(
                {
                    "event": "db_read_error",
                    "error": str(exc.__class__.__name__),
                }
            )
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch logs",
        ) from exc


def create_app() -> FastAPI:
    app = FastAPI(title="logmera", version="0.1.3")

    @app.on_event("startup")
    async def _startup() -> None:
        await init_db()

    if DASHBOARD_DIR.exists():
        app.mount("/dashboard", StaticFiles(directory=str(DASHBOARD_DIR)), name="dashboard")

    app.include_router(router)
    return app
