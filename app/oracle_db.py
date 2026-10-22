"""
Digital Legacy Vault - Oracle Database Module
Provides isolated connection handling, Thick mode client initialization,
and parameterized operations for Oracle Database 11g XE.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import oracledb
from app.config import settings

logger = logging.getLogger("digital_legacy.oracle")

# Module-level state tracking
_client_initialized = False
_client_init_error: Optional[str] = None


class OracleDatabaseError(Exception):
    """Base exception for Oracle database operations."""
    pass


class OracleNotConfiguredError(OracleDatabaseError):
    """Raised when required Oracle credentials are not set in environment."""
    pass


class OracleDriverError(OracleDatabaseError):
    """Raised when the Oracle client library or driver cannot be initialized."""
    pass


class OracleDuplicateError(OracleDatabaseError):
    """Raised when an Oracle unique constraint (ORA-00001) is violated."""
    pass


class OracleCompensationError(OracleDatabaseError):
    """Raised when a compensating delete fails during dual-write rollback."""
    pass


def init_oracle_client() -> None:
    """
    Initialize python-oracledb Thick mode using the specified client library directory.
    Thick mode is required for compatibility with Oracle Database 11g XE.
    """
    global _client_initialized, _client_init_error

    if _client_initialized:
        return

    lib_dir = getattr(settings, "ORACLE_CLIENT_LIB_DIR", None)
    try:
        if lib_dir:
            oracledb.init_oracle_client(lib_dir=lib_dir)
        else:
            oracledb.init_oracle_client()
        _client_initialized = True
        _client_init_error = None
        logger.info(f"Oracle Thick Mode initialized with client library at: {lib_dir}")
    except Exception as e:
        _client_initialized = False
        _client_init_error = str(e)
        logger.warning(f"Could not initialize Oracle Thick Mode client: {e}")


def is_oracle_configured() -> bool:
    """Check if Oracle user and password credentials are set."""
    user = getattr(settings, "ORACLE_USER", "").strip()
    pwd = getattr(settings, "ORACLE_PASSWORD", "").strip()
    return bool(user and pwd)


def get_oracle_connection():
    """
    Establish and return an active connection to Oracle Database XE.
    Raises descriptive exceptions if unconfigured or unreachable.
    """
    if not is_oracle_configured():
        raise OracleNotConfiguredError(
            "Oracle credentials not configured. Please set ORACLE_USER and ORACLE_PASSWORD in .env."
        )

    # Ensure thick mode initialization has been attempted
    init_oracle_client()
    if _client_init_error and not _client_initialized:
        raise OracleDriverError(
            f"Oracle Thick Mode client initialization failed: {_client_init_error}. "
            "Note: Oracle 11g XE requires Oracle Instant Client 19c+ or compatible OCI libraries."
        )

    try:
        connection = oracledb.connect(
            user=settings.ORACLE_USER,
            password=settings.ORACLE_PASSWORD,
            dsn=settings.ORACLE_DSN
        )
        return connection
    except oracledb.Error as e:
        error_obj, = e.args
        logger.error(f"Oracle connection error [Code {error_obj.code}]: {error_obj.message}")
        raise OracleDatabaseError(f"Failed to connect to Oracle at {settings.ORACLE_DSN}: {error_obj.message}") from e


def check_oracle_health() -> Dict[str, Any]:
    """
    Health check helper for Oracle Database connectivity.
    Returns status dictionary suitable for reporting.
    """
    if not is_oracle_configured():
        return {
            "configured": False,
            "connected": False,
            "message": "Oracle credentials not configured in .env"
        }

    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT instance_name, status, version FROM v$instance")
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        return {
            "configured": True,
            "connected": True,
            "instance": row[0] if row else "unknown",
            "status": row[1] if row else "unknown",
            "version": row[2] if row else "unknown"
        }
    except Exception as e:
        return {
            "configured": True,
            "connected": False,
            "message": str(e)
        }


def insert_oracle_user(
    user_id: str,
    name: str,
    email: str,
    phone: Optional[str],
    status: str,
    created_at: datetime
) -> Dict[str, Any]:
    """
    Persist a new user into Oracle USERS table using parameterized SQL.
    Commits on success; rolls back and handles constraint violations on failure.
    """
    conn = get_oracle_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO USERS (user_id, name, email, phone, status, created_at)
    VALUES (:user_id, :name, :email, :phone, :status, :created_at)
    """

    # Format created_at date for Oracle DATE type
    created_at_date = created_at if isinstance(created_at, datetime) else datetime.now(timezone.utc)
    # Remove timezone for standard Oracle DATE column compatibility if naive
    if created_at_date.tzinfo is not None:
        created_at_date = created_at_date.astimezone(timezone.utc).replace(tzinfo=None)

    params = {
        "user_id": user_id,
        "name": name,
        "email": email.lower().strip(),
        "phone": phone or "",
        "status": status,
        "created_at": created_at_date
    }

    try:
        cursor.execute(sql, params)
        conn.commit()
        logger.info(f"Successfully persisted user '{user_id}' ({email}) to Oracle USERS table.")
        return params
    except oracledb.IntegrityError as ie:
        conn.rollback()
        error_obj, = ie.args
        if error_obj.code == 1:  # ORA-00001: unique constraint violated
            raise OracleDuplicateError(
                f"Duplicate record in Oracle: User with ID '{user_id}' or email '{email}' already exists."
            ) from ie
        raise OracleDatabaseError(f"Oracle integrity constraint violated: {error_obj.message}") from ie
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to insert user '{user_id}' into Oracle: {e}")
        raise OracleDatabaseError(f"Oracle write operation failed: {str(e)}") from e
    finally:
        cursor.close()
        conn.close()


def delete_oracle_user(user_id: str) -> bool:
    """
    Compensating delete helper: Removes a user from Oracle USERS table
    if the secondary Neo4j write fails during dual-write coordination.
    """
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM USERS WHERE user_id = :user_id"
        cursor.execute(sql, {"user_id": user_id})
        conn.commit()
        row_count = cursor.rowcount
        cursor.close()
        conn.close()
        logger.info(f"Compensating delete executed on Oracle for user_id='{user_id}' (rows deleted: {row_count}).")
        return True
    except Exception as e:
        logger.critical(
            f"RECONCILIATION REQUIRED: Compensating delete on Oracle failed for user_id='{user_id}'. "
            f"Error: {e}. An orphan row remains in Oracle USERS table."
        )
        raise OracleCompensationError(
            f"Compensating delete failed for user_id='{user_id}'. Error: {str(e)}"
        ) from e


def get_oracle_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single user from Oracle USERS table by user_id."""
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        sql = """
        SELECT user_id, name, email, phone, status, created_at 
        FROM USERS 
        WHERE user_id = :user_id
        """
        cursor.execute(sql, {"user_id": user_id})
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return None

        return {
            "user_id": row[0],
            "name": row[1],
            "email": row[2],
            "phone": row[3],
            "status": row[4],
            "created_at": row[5].isoformat() if hasattr(row[5], "isoformat") else str(row[5])
        }
    except Exception as e:
        logger.error(f"Error fetching user '{user_id}' from Oracle: {e}")
        raise
