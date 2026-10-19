from pathlib import Path

PROJ_ROOT_DIR = Path().cwd().parent
SQLITE_SCHEMA_FILE = PROJ_ROOT_DIR / "schema" / "create_countries.sql"
SQLITE_DB_FILE = PROJ_ROOT_DIR / "data" / "processed" / "countries.db"
