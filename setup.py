from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).parent
README_PATH = BASE_DIR / "README.md"

setup(
    name="logmera",
    version="0.1.5",
    description="Self-hosted AI observability backend",
    long_description=README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else "",
    long_description_content_type="text/markdown",
    packages=find_packages(include=["logmera", "logmera.*"]),
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.116.0",
        "uvicorn>=0.35.0",
        "sqlalchemy>=2.0.0",
        "asyncpg>=0.29.0",
        "pydantic>=2.7.0",
        "typer>=0.12.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "logmera=logmera.cli:start",
        ]
    },
)
