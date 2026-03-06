from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CONFIGS_DIR = REPO_ROOT / "configs"
DBT_DIR = REPO_ROOT / "dbt"
DOCS_DIR = REPO_ROOT / "docs"


def raw_source_dir(source_name: str) -> Path:
    return RAW_DIR / source_name


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
