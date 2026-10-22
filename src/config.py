from pathlib import Path

# project root directory
PROJ_ROOT_DIR = Path().cwd().parent

# schema for SQLite database
SQLITE_SCHEMA_FILE = PROJ_ROOT_DIR / "schema" / "create_countries.sql"
# SQLite DB database file
SQLITE_DB_FILE = PROJ_ROOT_DIR / "data" / "processed" / "countries.db"

# Global Findex file from Data360
FINDEX_DATA360 = PROJ_ROOT_DIR / "data" / "raw" / "WB_FINDEX_20_IV_2026.csv"
# Global Findex from databank.worldbank.org for stratification codes and descriptions
# The series are fin45 group
FINDEX_FIN45 = PROJ_ROOT_DIR / "data" / "raw" / "fin45_Data.csv"
