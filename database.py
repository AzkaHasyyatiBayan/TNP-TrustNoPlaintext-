import sqlite3
import os
from datetime import datetime, timezone

DB_FILE = os.path.join(os.path.dirname(__file__), "krypto_audit.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if not already present."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                input_type TEXT NOT NULL,
                cipher TEXT NOT NULL,
                item_name TEXT NOT NULL,
                original_size INTEGER NOT NULL,
                result_size INTEGER NOT NULL,
                input_sha256 TEXT NOT NULL,
                output_sha256 TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                status TEXT NOT NULL,
                notes TEXT
            )
        """)
        conn.commit()

def log_operation(
    operation: str,
    input_type: str,
    cipher: str,
    item_name: str,
    original_size: int,
    result_size: int,
    input_sha256: str,
    output_sha256: str,
    duration_ms: float,
    status: str = "SUCCESS",
    notes: str = ""
) -> int:
    """Inserts a new audit log record and returns its ID."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (
                timestamp, operation, input_type, cipher, item_name,
                original_size, result_size, input_sha256, output_sha256,
                duration_ms, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_iso, operation.upper(), input_type.upper(), cipher, item_name,
            original_size, result_size, input_sha256, output_sha256,
            round(duration_ms, 2), status.upper(), notes
        ))
        conn.commit()
        return cursor.lastrowid

def get_recent_logs(limit: int = 50) -> list[dict]:
    """Retrieves the most recent audit logs."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def clear_logs():
    """Wipes all audit logs and resets autoincrement counter."""
    with get_connection() as conn:
        conn.execute("DELETE FROM audit_logs")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='audit_logs'")
        conn.commit()

def get_system_stats() -> dict:
    """Aggregates metrics for dashboard display."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total_ops, COALESCE(SUM(original_size), 0) as total_bytes FROM audit_logs")
        row = cursor.fetchone()
        total_ops = row["total_ops"]
        total_bytes = row["total_bytes"]

        cursor.execute("""
            SELECT cipher, COUNT(*) as count
            FROM audit_logs
            GROUP BY cipher
            ORDER BY count DESC
            LIMIT 5
        """)
        top_ciphers = [dict(r) for r in cursor.fetchall()]

        return {
            "total_operations": total_ops,
            "total_bytes_processed": total_bytes,
            "top_ciphers": top_ciphers
        }
