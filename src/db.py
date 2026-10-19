import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def connection(db_file: Path):
    '''
    Open a db_file only if it exists. Otherwise raise OperationalError.
    Ensure foreign keys are on.
    Always close the connection.
    '''
    # resolve a path in case it's relative and change into uri format
    uri_db_file = db_file.resolve().as_uri()
    # connect do a db if it exists
    conn = sqlite3.connect(f"{uri_db_file}?mode=rw", uri=True)
    # ensure foreign keys
    try:
        conn.execute("pragma foreign_keys = on;")
        # transaction commits or rolls back
        with conn:    
            yield conn
    # always close the connection
    finally:
        conn.close()

def ensure_db(db_file: Path, db_schema_file: Path) -> None:
    '''
    Create a DB using the provided schema if it doesn't exist.
    The DB is created as one transaction which either comits or rolls back.
    It is assumed that schema has begin/commit.
    '''
    # if the db exists do nothing
    if db_file.is_file(): return
    
    # ensure the directory exists
    # create one with all the parents unless it already exists
    db_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(db_file)
        try:
            conn.executescript(db_schema_file.read_text())
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except Exception:
        # remove DB because it was not initialized correctly
        db_file.unlink(missing_ok=True)
        raise

def ensure_source(db_file: Path, source_code: str, source_name: str) -> None:
    with connection(db_file) as conn:
        # uses SQLite dialect ON CONFLICT clause
        # if constraints are violated it does nothing
        conn.execute(
            """
            INSERT INTO sources (
                source_code,
                source_name
            )
            VALUES (?, ?)
            ON CONFLICT DO NOTHING;
            """,
            (
                source_code,
                source_name
            )
        )
        # check source
        # there's a primary key constraint on source_code
        row = conn.execute(
            """
            select * from sources
            where source_code = ?;
            """,
            (source_code, )
        ).fetchone()

        if row is None:
            raise sqlite3.IntegrityError(
                f"Source {source_code!r} was not found after insertion."
            )

        if row != (source_code, source_name):
            raise ValueError(
                f"source_code: {row[0]!r} has an unexpected name {row[1]!r}."
            )
