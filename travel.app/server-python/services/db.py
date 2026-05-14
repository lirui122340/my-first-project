import os
import psycopg2
from psycopg2.extras import DictCursor

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'travel_app'),
}


def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f'数据库连接失败: {e}')
        return None


def execute_query(sql, params=None):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql, params)
            if cursor.description:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            return []
    except Exception as e:
        print(f'数据库查询失败: {e}')
        return []
    finally:
        conn.close()


def execute_query_one(sql, params=None):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql, params)
            if cursor.description:
                row = cursor.fetchone()
                return dict(row) if row else None
            return None
    except Exception as e:
        print(f'数据库查询失败: {e}')
        return None
    finally:
        conn.close()


def execute_update(sql, params=None):
    conn = get_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
    except Exception as e:
        print(f'数据库更新失败: {e}')
        return 0
    finally:
        conn.close()
